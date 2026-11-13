#!/usr/bin/env python3
"""中证500单因子自然周收益回测引擎。

行情统一读取 data/zz500 下的 stock_day、指数和交易状态分区。
因子以 ``available_date <= rebalance_date`` 为唯一可用性条件，绝不以
``signal_date`` 代替可用日期。每个因子同时运行 higher/lower 两个方向。
"""

from __future__ import annotations

from dataloader import read_constituent_table, read_trading_status, read_parquet_table, DEFAULT_TRADING_STATUS_PATH, DEFAULT_STOCK_DAY_PATH, DEFAULT_INDEX_PATH

from dataloader import portable_path, portable_payload
import hashlib
import json
import math
import os
import shutil
import tempfile
import traceback
import uuid
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from dataloader import read_factor_output, write_output_parquet


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_EXECUTION_PRICES = DEFAULT_STOCK_DAY_PATH
DEFAULT_BENCHMARK = DEFAULT_INDEX_PATH


ENGINE_VERSION = "weekly_factor_return_report_portfolios_v6"
DIRECTIONS = ("higher", "lower")
SECURITY_CODE_ALIASES = {
    "000022.SZ": "001872.SZ",
    "601313.SH": "601360.SH",
    "000043.SZ": "001914.SZ",
    "300114.SZ": "302132.SZ",
}
@dataclass(frozen=True)
class WeekPeriod:
    week_id: str
    iso_year: int
    iso_week: int
    first_trade: pd.Timestamp
    last_trade: pd.Timestamp


@dataclass
class MarketContext:
    requested_start: pd.Timestamp
    requested_end: pd.Timestamp
    periods: tuple[WeekPeriod, ...]
    symbols: tuple[str, ...]
    symbol_to_position: dict[str, int]
    first_dates: np.ndarray
    last_dates: np.ndarray
    member_mask: np.ndarray
    candidate_mask: np.ndarray
    tradeable_mask: np.ndarray
    first_close: np.ndarray
    last_close: np.ndarray
    benchmark_first_close: np.ndarray
    benchmark_last_close: np.ndarray
    source_paths: dict[str, str]


def _round_cent(values: np.ndarray | float) -> np.ndarray | float:
    return np.floor(np.asarray(values, dtype="float64") * 100.0 + 0.5) / 100.0


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_write_json(payload: dict[str, Any], path: Path) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(portable_payload(payload), handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        os.replace(temporary_name, path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def _read_constituents(
    path: Path,
    symbol_aliases: dict[str, str] | None = None,
) -> tuple[pd.DatetimeIndex, dict[pd.Timestamp, tuple[str, ...]]]:
    frame = read_constituent_table(path)
    if frame.empty or frame["date"].duplicated().any():
        raise ValueError(f"逐日成分股为空或日期重复: {path}")
    frame = frame.sort_values("date")
    members: dict[pd.Timestamp, tuple[str, ...]] = {}
    aliases = symbol_aliases or {}
    for row in frame.itertuples(index=False):
        tickers = tuple(
            sorted(
                aliases.get(value.strip(), value.strip())
                for value in str(row.tickers or "").split(",")
                if value.strip()
            )
        )
        members[pd.Timestamp(row.date)] = tickers
    return pd.DatetimeIndex(frame["date"]), members


def _build_periods(
    calendar: pd.DatetimeIndex,
    requested_start: pd.Timestamp,
    requested_end: pd.Timestamp,
) -> tuple[WeekPeriod, ...]:
    if requested_start > requested_end:
        raise ValueError("start不能晚于end")
    available = calendar[calendar <= requested_end]
    if available.empty:
        raise ValueError("请求区间没有交易日")

    grouped: dict[pd.Period, list[pd.Timestamp]] = {}
    for trading_day in calendar:
        grouped.setdefault(trading_day.to_period("W-SUN"), []).append(trading_day)

    absolute_last = calendar[-1]
    final_period = absolute_last.to_period("W-SUN")
    periods: list[WeekPeriod] = []
    for natural_week, dates in sorted(grouped.items()):
        first_trade = dates[0]
        last_trade = dates[-1]
        if first_trade < requested_start or last_trade > requested_end:
            continue
        # 数据集若在周中结束，最后这个自然周不能被误判为完整周。
        if natural_week == final_period and absolute_last.weekday() < 4:
            continue
        iso = last_trade.isocalendar()
        periods.append(
            WeekPeriod(
                week_id=f"{int(iso.year):04d}-W{int(iso.week):02d}",
                iso_year=int(iso.year),
                iso_week=int(iso.week),
                first_trade=first_trade,
                last_trade=last_trade,
            )
        )
    if not periods:
        raise ValueError("请求区间没有完整自然周")
    return tuple(periods)


def _load_price_matrices(
    execution_prices: Path,
    periods: tuple[WeekPeriod, ...],
    symbols: tuple[str, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    dates = sorted({p.first_trade for p in periods} | {p.last_trade for p in periods})
    frame = read_parquet_table(execution_prices, ["trade_date", "ts_code", "close", "vol"],
                               dates=dates, symbols=symbols)
    if frame.duplicated(["trade_date", "ts_code"]).any():
        raise ValueError("执行行情存在重复日期/股票代码")
    prices = frame.pivot(index="trade_date", columns="ts_code", values="close")
    volumes = frame.pivot(index="trade_date", columns="ts_code", values="vol")
    first_dates = [p.first_trade for p in periods]
    last_dates = [p.last_trade for p in periods]
    first_close = prices.reindex(index=first_dates, columns=symbols).to_numpy(dtype=float)
    last_close = prices.reindex(index=last_dates, columns=symbols).to_numpy(dtype=float)
    first_volume = volumes.reindex(index=first_dates, columns=symbols).to_numpy(dtype=float)
    first_close[~np.isfinite(first_close) | (first_close <= 0)] = np.nan
    last_close[~np.isfinite(last_close) | (last_close <= 0)] = np.nan
    # 有行情但成交量缺失时按0处理，不允许交易。
    present = frame.assign(present=True).pivot(index="trade_date", columns="ts_code", values="present")
    present = present.reindex(index=first_dates, columns=symbols).eq(True).to_numpy(dtype=bool)
    first_volume[np.isnan(first_volume) & present] = 0.0
    first_volume[~np.isfinite(first_volume) | (first_volume < 0)] = np.nan
    return first_close, first_volume, last_close


def _load_status_masks(
    status_path: Path,
    periods: tuple[WeekPeriod, ...],
    symbol_to_position: dict[str, int],
) -> tuple[np.ndarray, np.ndarray]:
    """只使用ST和停牌；上市状态不参与交易筛选，空值默认正常。"""
    dates = pd.DatetimeIndex(period.first_trade for period in periods)
    symbols = sorted(symbol_to_position, key=symbol_to_position.get)
    status = read_trading_status(status_path, dates=dates, symbols=symbols)
    def matrix(column):
        panel = status.pivot(index="trade_date", columns="ts_code", values=column)
        return panel.reindex(index=dates, columns=symbols).astype("boolean").fillna(False).to_numpy(dtype=bool)
    return matrix("is_suspended"), matrix("is_st")


def _load_benchmark(
    path: Path,
    periods: tuple[WeekPeriod, ...],
    benchmark_index: str,
) -> tuple[np.ndarray, np.ndarray]:
    frame = read_parquet_table(path, ["trade_date", "ts_code", "close"],
                               dates=[d for period in periods for d in (period.first_trade, period.last_trade)],
                               symbols=[benchmark_index])
    if frame.trade_date.duplicated().any():
        raise ValueError("基准指数存在重复日期")
    values = pd.to_numeric(frame.set_index("trade_date")["close"], errors="coerce")
    first = values.reindex([period.first_trade for period in periods]).to_numpy(dtype="float64")
    last = values.reindex([period.last_trade for period in periods]).to_numpy(dtype="float64")
    if not np.isfinite(first).all() or not np.isfinite(last).all() or (first<=0).any() or (last<=0).any():
        raise ValueError(
            f"基准 {benchmark_index} 缺少自然周首日或末日收盘价"
        )
    return first, last


def build_market_context(
    *,
    constituents_path: Path,
    status_path: Path = DEFAULT_TRADING_STATUS_PATH,
    execution_prices: Path,
    benchmark_path: Path,
    start: str,
    end: str | None,
    benchmark_index: str = "000905.SH",
) -> MarketContext:
    """一次性构建所有因子共享的自然周行情和资格矩阵。"""
    member_calendar, members = _read_constituents(constituents_path)
    index_days = read_parquet_table(benchmark_path, ["trade_date", "ts_code"], symbols=[benchmark_index])
    if index_days.trade_date.duplicated().any():
        raise ValueError("基准指数存在重复交易日")
    calendar = pd.DatetimeIndex(index_days.trade_date).sort_values()
    if calendar.empty:
        raise ValueError(f"指数行情为空: {benchmark_index}")
    requested_start = pd.Timestamp(start).normalize()
    requested_end = (
        pd.Timestamp(end).normalize() if end else pd.Timestamp(calendar[-1]).normalize()
    )
    missing_members = calendar[(calendar >= requested_start) & (calendar <= requested_end)].difference(member_calendar)
    if len(missing_members):
        raise ValueError(f"指数交易日缺少成分股名单: {missing_members[:5].tolist()}")
    periods = _build_periods(calendar, requested_start, requested_end)
    symbols = tuple(
        sorted(
            {
                ticker
                for period in periods
                for ticker in members.get(period.first_trade, ())
            }
        )
    )
    symbol_to_position = {symbol: position for position, symbol in enumerate(symbols)}
    member_mask = np.zeros((len(periods), len(symbols)), dtype=bool)
    for row_position, period in enumerate(periods):
        for ticker in members.get(period.first_trade, ()):
            column_position = symbol_to_position.get(ticker)
            if column_position is not None:
                member_mask[row_position, column_position] = True

    first_close, first_volume, last_close = _load_price_matrices(execution_prices, periods, symbols)
    suspended, is_st = _load_status_masks(status_path, periods, symbol_to_position)
    has_execution_price = np.isfinite(first_close) & (first_close > 0.0)
    has_volume = np.isfinite(first_volume) & (first_volume > 0.0)
    tradeable_mask = has_execution_price & has_volume & ~suspended
    candidate_mask = member_mask & tradeable_mask & ~is_st
    benchmark_first, benchmark_last = _load_benchmark(benchmark_path, periods, benchmark_index)
    return MarketContext(
        requested_start=requested_start,
        requested_end=requested_end,
        periods=periods,
        symbols=symbols,
        symbol_to_position=symbol_to_position,
        first_dates=np.asarray(
            [period.first_trade.to_datetime64() for period in periods],
            dtype="datetime64[D]",
        ),
        last_dates=np.asarray(
            [period.last_trade.to_datetime64() for period in periods],
            dtype="datetime64[D]",
        ),
        member_mask=member_mask,
        candidate_mask=candidate_mask,
        tradeable_mask=tradeable_mask,
        first_close=first_close,
        last_close=last_close,
        benchmark_first_close=benchmark_first,
        benchmark_last_close=benchmark_last,
        source_paths={
            "constituents": portable_path(constituents_path),
            "security_status": portable_path(status_path),
            "execution_prices": portable_path(execution_prices),
            "benchmark": portable_path(benchmark_path),
            "benchmark_index": benchmark_index,
        },
    )




def inspect_factor_source(factor_dir: Path, versions=("raw", "neutralization")) -> tuple[bool, str, int]:
    try:
        frames = [read_factor_output(factor_dir, v) for v in versions]
        if len(frames) == 2 and (not frames[0].iloc[:, :2].equals(frames[1].iloc[:, :2]) or list(frames[0].columns) != list(frames[1].columns)):
            return False, "version_grid_mismatch", 2
        return True, "ready", len(versions)
    except (OSError, ValueError) as error:
        return False, f"factor_parquet_invalid: {error}", 0


def _load_factor_snapshots(factor_dir: Path, context: MarketContext,
                           version: str = "neutralization", frame: pd.DataFrame | None = None
                           ) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    # 保留起点之前的可用快照，只限制股票列与最晚购买日。
    if frame is None:
        frame = read_factor_output(factor_dir, version, symbols=context.symbols,
                                   end=max(context.first_dates) if len(context.first_dates) else None)
    shape = (len(context.periods), len(context.symbols))
    values = np.full(shape, np.nan, dtype="float64")
    used_available = np.full(shape, np.datetime64("NaT"), dtype="datetime64[D]")
    used_signal = used_available.copy()
    valid = frame.signal_date.notna() & frame.available_date.notna()
    frame = frame.loc[valid].sort_values(["available_date", "signal_date"], kind="mergesort")
    if frame.empty:
        return values, used_available, used_signal, 1
    available = frame.available_date.to_numpy(dtype="datetime64[D]")
    signal = frame.signal_date.to_numpy(dtype="datetime64[D]")
    positions = np.searchsorted(available, context.first_dates, side="right") - 1
    usable = positions >= 0
    positions = positions[usable]
    if np.any(available[positions] > context.first_dates[usable]) or np.any(signal[positions] > context.first_dates[usable]):
        raise AssertionError("检测到因子日期晚于购买日")
    for symbol, column in context.symbol_to_position.items():
        if symbol in frame:
            values[usable, column] = pd.to_numeric(frame[symbol], errors="coerce").to_numpy(dtype="float64")[positions]
            used_available[usable, column] = available[positions]
            used_signal[usable, column] = signal[positions]
    return values, used_available, used_signal, 1


def _fees(side: str, gross: np.ndarray) -> np.ndarray:
    if gross.size == 0:
        return np.asarray([], dtype="float64")
    commission = _round_cent(np.maximum(gross * 0.0003, 5.0))
    transfer = _round_cent(gross * 0.00001)
    stamp = _round_cent(gross * 0.001) if side == "sell" else np.zeros_like(gross)
    return commission + transfer + stamp


def _mark_equity(
    cash: float,
    shares: np.ndarray,
    prices: np.ndarray,
    last_marks: np.ndarray,
) -> tuple[float, np.ndarray]:
    marks = np.where(np.isfinite(prices) & (prices > 0.0), prices, last_marks)
    held = shares > 0
    if np.any(held & (~np.isfinite(marks) | (marks <= 0.0))):
        missing = np.flatnonzero(held & (~np.isfinite(marks) | (marks <= 0.0)))
        raise ValueError(f"持仓缺少估值价格，列位置: {missing[:10].tolist()}")
    updated_marks = np.where(np.isfinite(prices) & (prices > 0.0), prices, last_marks)
    equity = float(cash + np.dot(shares.astype("float64"), np.nan_to_num(marks)))
    return equity, updated_marks


def _rebalance(
    *,
    cash: float,
    shares: np.ndarray,
    selected: np.ndarray,
    prices: np.ndarray,
    tradeable: np.ndarray,
    last_marks: np.ndarray,
    lot_size: int,
) -> tuple[float, np.ndarray, dict[str, float | int]]:
    pretrade_equity, last_marks = _mark_equity(cash, shares, prices, last_marks)
    held = shares > 0
    stuck = held & ~tradeable
    stuck_value = float(
        np.dot(shares[stuck].astype("float64"), last_marks[stuck])
    )
    selected_tradeable = selected & tradeable
    selected_count = int(selected_tradeable.sum())
    target_shares = np.zeros_like(shares)
    if selected_count:
        allocatable = max(pretrade_equity - stuck_value, 0.0)
        target_value = allocatable / selected_count
        target_lots = np.floor(
            target_value / (prices[selected_tradeable] * lot_size) + 0.5
        ).astype("int64")
        target_shares[selected_tradeable] = target_lots * lot_size
    target_shares[stuck] = shares[stuck]

    difference = target_shares - shares
    sell_positions = np.flatnonzero((difference < 0) & tradeable)
    sell_volume = (-difference[sell_positions]).astype("int64")
    sell_gross = sell_volume.astype("float64") * prices[sell_positions]
    sell_fees = _fees("sell", sell_gross)
    if sell_positions.size:
        cash += float(sell_gross.sum() - sell_fees.sum())
        shares[sell_positions] -= sell_volume

    buy_positions = np.flatnonzero((target_shares - shares > 0) & tradeable)
    buy_volume = (target_shares[buy_positions] - shares[buy_positions]).astype("int64")
    if buy_positions.size:
        buy_gross = buy_volume.astype("float64") * prices[buy_positions]
        buy_fees = _fees("buy", buy_gross)
        total_cost = float(buy_gross.sum() + buy_fees.sum())
        # 目标权重使用满仓资产，费用和整手四舍五入可能造成现金不足。
        # 确定性地从证券代码靠后的订单逐手缩减，直到全部订单可成交。
        cursor = len(buy_positions) - 1
        while total_cost > cash + 1e-8 and buy_positions.size:
            if buy_volume[cursor] >= lot_size:
                buy_volume[cursor] -= lot_size
            cursor -= 1
            if cursor < 0:
                cursor = len(buy_positions) - 1
            positive = buy_volume > 0
            buy_positions = buy_positions[positive]
            buy_volume = buy_volume[positive]
            if not buy_positions.size:
                buy_gross = np.asarray([], dtype="float64")
                buy_fees = np.asarray([], dtype="float64")
                total_cost = 0.0
                break
            cursor = min(cursor, len(buy_positions) - 1)
            buy_gross = buy_volume.astype("float64") * prices[buy_positions]
            buy_fees = _fees("buy", buy_gross)
            total_cost = float(buy_gross.sum() + buy_fees.sum())
        if buy_positions.size:
            cash -= total_cost
            shares[buy_positions] += buy_volume
    else:
        buy_gross = np.asarray([], dtype="float64")
        buy_fees = np.asarray([], dtype="float64")

    cash = float(_round_cent(cash))
    if cash < -0.011:
        raise AssertionError(f"调仓后现金为负: {cash}")
    buy_amount = float(buy_gross.sum()) if buy_gross.size else 0.0
    sell_amount = float(sell_gross.sum()) if sell_gross.size else 0.0
    fees = float(buy_fees.sum() + sell_fees.sum())
    return cash, shares, {
        "pretrade_equity": pretrade_equity,
        "buy_order_count": int(buy_positions.size),
        "sell_order_count": int(sell_positions.size),
        "buy_amount": buy_amount,
        "sell_amount": sell_amount,
        "fees": fees,
        "one_way_turnover": (
            (buy_amount + sell_amount) / (2.0 * pretrade_equity)
            if pretrade_equity > 0.0
            else 0.0
        ),
    }


def _latest_date_text(values: np.ndarray, mask: np.ndarray) -> str:
    selected = values[mask]
    selected = selected[~np.isnat(selected)]
    if not selected.size:
        return ""
    return str(selected.max())


def _simulate_direction(
    *,
    factor_name: str,
    factor_column: str,
    direction: str,
    factor_values: np.ndarray,
    used_available: np.ndarray,
    used_signal: np.ndarray,
    context: MarketContext,
    initial_capital: float,
    minimum_coverage: float,
    lot_size: int,
    buy_fraction: float = 0.20,
    hold_fraction: float = 0.30,
    quintile: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    shares = np.zeros(len(context.symbols), dtype="int64")
    cash = float(initial_capital)
    last_marks = np.full(len(context.symbols), np.nan, dtype="float64")
    previous_end_equity = float(initial_capital)
    started = False
    rows: list[dict[str, Any]] = []
    cumulative_fees = 0.0
    cumulative_buy = 0.0
    cumulative_sell = 0.0

    for row_position, period in enumerate(context.periods):
        candidate = context.candidate_mask[row_position]
        finite = np.isfinite(factor_values[row_position])
        ranked_mask = candidate & finite
        eligible_count = int(candidate.sum())
        factor_count = int(ranked_mask.sum())
        coverage = factor_count / eligible_count if eligible_count else 0.0
        rebalanced = coverage + 1e-12 >= minimum_coverage and factor_count >= 3
        selected = np.zeros(len(context.symbols), dtype=bool)
        if rebalanced:
            valid_positions = np.flatnonzero(ranked_mask)
            valid_values = factor_values[row_position, valid_positions]
            sort_values = -valid_values if direction == "higher" else valid_values
            order = np.argsort(sort_values, kind="mergesort")
            ordered_positions = valid_positions[order]
            buy_count = max(1, math.ceil(len(ordered_positions) * buy_fraction))
            hold_count = max(buy_count, math.ceil(len(ordered_positions) * hold_fraction))
            if quintile in (2, 3, 4):
                n = len(ordered_positions)
                # 两端与higher/lower精确一致，中间三组构成无重叠的完整划分。
                tail = math.ceil(n * 0.20)
                edges = [0, tail, math.ceil(n*0.40), n-math.ceil(n*0.40), n-tail, n]
                left, right = edges[quintile-1:quintile+1]
                if right <= left:
                    raise ValueError("有效股票不足以形成五个非空分组")
                buffer = math.ceil(n*0.05)
                buy_zone = ordered_positions[left:right]
                hold_zone = ordered_positions[max(0,left-buffer):min(n,right+buffer)]
            else:
                buy_zone = ordered_positions[:buy_count]
                hold_zone = ordered_positions[:hold_count]
            selected[buy_zone] = True
            current_positions = np.flatnonzero(shares > 0)
            retained = np.intersect1d(
                current_positions, hold_zone, assume_unique=True
            )
            selected[retained] = True

        week_start_equity = previous_end_equity
        if rebalanced:
            cash, shares, audit = _rebalance(
                cash=cash,
                shares=shares,
                selected=selected,
                prices=context.first_close[row_position],
                tradeable=context.tradeable_mask[row_position],
                last_marks=last_marks,
                lot_size=lot_size,
            )
            _, last_marks = _mark_equity(
                cash, shares, context.first_close[row_position], last_marks
            )
            started = True
        else:
            pretrade_equity, last_marks = _mark_equity(
                cash, shares, context.first_close[row_position], last_marks
            )
            audit = {
                "pretrade_equity": pretrade_equity,
                "buy_order_count": 0,
                "sell_order_count": 0,
                "buy_amount": 0.0,
                "sell_amount": 0.0,
                "fees": 0.0,
                "one_way_turnover": 0.0,
            }

        end_equity, last_marks = _mark_equity(
            cash, shares, context.last_close[row_position], last_marks
        )
        weekly_return = end_equity / week_start_equity - 1.0
        if rows:
            benchmark_return = (
                context.benchmark_last_close[row_position]
                / context.benchmark_last_close[row_position - 1]
                - 1.0
            )
        else:
            benchmark_return = (
                context.benchmark_last_close[row_position]
                / context.benchmark_first_close[row_position]
                - 1.0
            )
        cumulative_fees += float(audit["fees"])
        cumulative_buy += float(audit["buy_amount"])
        cumulative_sell += float(audit["sell_amount"])

        if started:
            rows.append({
                "factor_name": factor_name,
                "factor_column": factor_column,
                "direction": direction,
                "week_id": period.week_id,
                "iso_year": period.iso_year,
                "iso_week": period.iso_week,
                "week_first_trade": period.first_trade.strftime("%Y-%m-%d"),
                "week_last_trade": period.last_trade.strftime("%Y-%m-%d"),
                "rebalance_date": period.first_trade.strftime("%Y-%m-%d"),
                "latest_signal_date_used": _latest_date_text(
                    used_signal[row_position], ranked_mask
                ),
                "latest_available_date_used": _latest_date_text(
                    used_available[row_position], ranked_mask
                ),
                "eligible_count": eligible_count,
                "factor_value_count": factor_count,
                "factor_coverage": coverage,
                "rebalanced": bool(rebalanced),
                "buy_order_count": int(audit["buy_order_count"]),
                "sell_order_count": int(audit["sell_order_count"]),
                "holding_count": int((shares > 0).sum()),
                "buy_amount": float(audit["buy_amount"]),
                "sell_amount": float(audit["sell_amount"]),
                "one_way_turnover": float(audit["one_way_turnover"]),
                "fees": float(audit["fees"]),
                "start_equity": week_start_equity,
                "pretrade_equity": float(audit["pretrade_equity"]),
                "end_equity": end_equity,
                "weekly_return": weekly_return,
                "benchmark_return": benchmark_return,
                "weekly_excess_return": (
                    (1.0 + weekly_return) / (1.0 + benchmark_return) - 1.0
                ),
                "cumulative_return": end_equity / initial_capital - 1.0,
            })
        previous_end_equity = end_equity

    if not rows:
        raise ValueError("整个请求区间都未达到最低因子覆盖率")
    returns = np.asarray([float(row["weekly_return"]) for row in rows])
    equities = np.asarray(
        [float(initial_capital), *[float(row["end_equity"]) for row in rows]],
        dtype="float64",
    )
    peaks = np.maximum.accumulate(equities)
    drawdowns = equities / peaks - 1.0
    first_date = pd.Timestamp(rows[0]["week_first_trade"])
    last_date = pd.Timestamp(rows[-1]["week_last_trade"])
    years = max((last_date - first_date).days / 365.25, 0.0)
    ending = float(rows[-1]["end_equity"])
    total_return = ending / initial_capital - 1.0
    benchmark_total = float(np.prod(1.0 + np.asarray(
        [float(row["benchmark_return"]) for row in rows], dtype="float64"
    )) - 1.0)
    volatility = float(np.std(returns, ddof=1) * math.sqrt(52)) if len(returns) > 1 else 0.0
    sharpe = (
        float(np.mean(returns) / np.std(returns, ddof=1) * math.sqrt(52))
        if len(returns) > 1 and np.std(returns, ddof=1) > 0.0
        else 0.0
    )
    summary = {
        "factor_name": factor_name,
        "factor_column": factor_column,
        "direction": direction,
        "requested_start": context.requested_start.strftime("%Y-%m-%d"),
        "requested_end": context.requested_end.strftime("%Y-%m-%d"),
        "effective_start": rows[0]["week_first_trade"],
        "effective_end": rows[-1]["week_last_trade"],
        "week_count": len(rows),
        "initial_capital": initial_capital,
        "ending_equity": ending,
        "total_return": total_return,
        "annualized_return": (
            (ending / initial_capital) ** (1.0 / years) - 1.0
            if years > 0.0 and ending > 0.0
            else 0.0
        ),
        "maximum_drawdown": float(drawdowns.min()),
        "annualized_weekly_volatility": volatility,
        "weekly_sharpe_zero_rate": sharpe,
        "positive_week_ratio": float(np.mean(returns > 0.0)),
        "benchmark_total_return": benchmark_total,
        "total_excess_return": (1.0 + total_return) / (1.0 + benchmark_total) - 1.0,
        "total_fees": cumulative_fees,
        "gross_buy_amount": cumulative_buy,
        "gross_sell_amount": cumulative_sell,
        "mean_one_way_turnover": float(np.mean([
            float(row["one_way_turnover"]) for row in rows
        ])),
        "rebalanced_week_count": int(sum(bool(row["rebalanced"]) for row in rows)),
        "minimum_factor_coverage": minimum_coverage,
        "buy_fraction": buy_fraction,
        "hold_fraction": hold_fraction,
        "quintile": quintile,
    }
    return rows, summary




def completed_factor_output(path: Path, factor_name: str, versions=("raw", "neutralization")) -> bool:
    try:
        metadata = json.loads((path / "metadata.json").read_text())
        if metadata.get("status") != "completed" or metadata.get("engine_version") != ENGINE_VERSION or metadata.get("factor_name") != factor_name:
            return False
        if metadata.get("factor_versions") != list(versions):
            return False
        for version in versions:
            frame = pd.read_parquet(path / f"{version}.parquet")
            if list(frame.columns) != ["week_id", "week_first_trade", "week_last_trade", "higher", "lower"] or frame.empty or frame.week_id.duplicated().any():
                return False
            if not np.isfinite(frame[["higher", "lower"]].to_numpy(dtype=float)).all():
                return False
        return True
    except Exception:
        return False


def run_factor(
    *,
    factor_name: str,
    factor_source_root: Path,
    output_root: Path,
    context: MarketContext,
    initial_capital: float,
    minimum_coverage: float,
    lot_size: int = 100,
    versions: tuple[str, ...] = ("raw", "neutralization"),
) -> dict[str, Any]:
    """运行一个因子的双方向回测并原子落盘。"""
    destination = output_root / factor_name
    try:
        if destination.exists():
            if completed_factor_output(destination, factor_name, versions):
                return {"factor": factor_name, "status": "already_completed"}
            raise FileExistsError(f"因子输出目录已存在但不完整: {destination}")
        if versions not in (("raw", "neutralization"), ("raw",), ("neutralization",)):
            raise ValueError("不支持的版本组合")
        factor_dir = factor_source_root / factor_name
        ready, reason, file_count = inspect_factor_source(factor_dir, versions)
        if not ready:
            return {
                "factor": factor_name,
                "status": "skipped",
                "reason": reason,
                "factor_file_count": file_count,
            }
        tables = {}
        version_summaries = {}
        benchmark_weekly = {}
        for version in versions:
            factor_values, used_available, used_signal, files_read = _load_factor_snapshots(
                factor_dir, context, version)
            if not np.isfinite(factor_values).any():
                return {"factor": factor_name, "status": "skipped", "reason": f"{version}_values_all_missing"}
            summaries = []
            parts = []
            benchmark_weekly[version] = {}
            for direction in DIRECTIONS:
                rows, summary = _simulate_direction(
                    factor_name=factor_name, factor_column=f"{factor_name}_{version}",
                    direction=direction, factor_values=factor_values,
                    used_available=used_available, used_signal=used_signal, context=context,
                    initial_capital=initial_capital, minimum_coverage=minimum_coverage, lot_size=lot_size)
                compounded = float(np.prod(1.0 + np.asarray([r["weekly_return"] for r in rows])) - 1.0)
                if not math.isclose(compounded, summary["total_return"], rel_tol=1e-10, abs_tol=1e-10):
                    raise AssertionError("周收益复利与总收益不一致")
                frame = pd.DataFrame(rows)
                for column in ("week_first_trade", "week_last_trade"):
                    frame[column] = pd.to_datetime(frame[column])
                benchmark_weekly[version].update(dict(zip(frame.week_id, frame.benchmark_return)))
                parts.append(frame.set_index(["week_id", "week_first_trade", "week_last_trade"])["weekly_return"].rename(direction))
                summaries.append(summary)
            table = pd.concat(parts, axis=1).sort_index().reset_index()
            if table[["higher", "lower"]].isna().any().any():
                raise ValueError(f"{version} 双方向回测有效周不一致，不能提交不完整收益表")
            tables[version] = table
            version_summaries[version] = summaries

        output_root.mkdir(parents=True, exist_ok=True)
        temporary = output_root / f".{factor_name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
        temporary.mkdir()
        try:
            for version, frame in tables.items():
                write_output_parquet(frame, temporary / f"{version}.parquet")
            metadata = {
                "status": "completed",
                "engine_version": ENGINE_VERSION,
                "factor_name": factor_name,
                "factor_versions": list(versions),
                "summary": version_summaries,
                "benchmark_weekly_returns": benchmark_weekly,
                "factor_source": portable_path(factor_dir),
                "factor_file_count": file_count,
                "factor_files_read": files_read,
                "directions": list(DIRECTIONS),
                "requested_start": context.requested_start.strftime("%Y-%m-%d"),
                "requested_end": context.requested_end.strftime("%Y-%m-%d"),
                "natural_week_policy": (
                    "only weeks whose first and last exchange trading dates are both "
                    "inside the requested interval"
                ),
                "rebalance_policy": "first trading day close",
                "valuation_policy": "last trading day close",
                "availability_policy": (
                    "latest observation satisfying available_date <= rebalance_date; "
                    "signal_date is audit metadata only"
                ),
                "factor_version": "_and_".join(versions),
                "buy_rule": "top_20_percent",
                "hold_rule": "existing holding remains inside top_30_percent",
                "weighting": "equal_weight",
                "minimum_factor_coverage": minimum_coverage,
                "initial_capital": initial_capital,
                "lot_size": lot_size,
                "fees": {
                    "commission_rate": 0.0003,
                    "minimum_commission": 5.0,
                    "transfer_fee_rate": 0.00001,
                    "stamp_tax_rate_on_sell": 0.001,
                },
                "source_paths": context.source_paths,
                "engine_sha256": _sha256_file(Path(__file__).resolve()),
            }
            _atomic_write_json(metadata, temporary / "metadata.json")
            temporary.replace(destination)
        except BaseException:
            shutil.rmtree(temporary, ignore_errors=True)
            raise
        summaries = version_summaries["neutralization"] if "neutralization" in version_summaries else version_summaries["raw"]
        return {
            "factor": factor_name,
            "status": "completed",
            "weeks_higher": summaries[0]["week_count"],
            "weeks_lower": summaries[1]["week_count"],
            "return_higher": summaries[0]["total_return"],
            "return_lower": summaries[1]["total_return"],
        }
    except Exception:
        return {
            "factor": factor_name,
            "status": "failed",
            "traceback": traceback.format_exc(),
        }


def report_return_signature(context: MarketContext, initial_capital: float,
                            minimum_coverage: float, lot_size: int) -> dict[str, Any]:
    digest=hashlib.sha256()
    for field in ("first_dates","last_dates","member_mask","candidate_mask","tradeable_mask",
                  "first_close","last_close","benchmark_first_close","benchmark_last_close"):
        array=getattr(context,field)
        digest.update(field.encode());digest.update(array.tobytes())
    return {"engine_version": ENGINE_VERSION, "engine_sha256": _sha256_file(Path(__file__)),
            "market_context_sha256":digest.hexdigest(),
            "requested_start": str(context.requested_start.date()),
            "requested_end": str(context.requested_end.date()),
            "initial_capital": initial_capital, "minimum_factor_coverage": minimum_coverage,
            "lot_size": lot_size, "source_paths": context.source_paths}


def report_returns_ready(path: Path, signature: dict[str, Any]) -> bool:
    try:
        meta = json.loads((path/"report_return_metadata.json").read_text())
        frame = pd.read_parquet(path/"report_portfolios.parquet", columns=["portfolio", "week_id"])
        return (meta.get("signature") == portable_payload(signature) and meta.get("status") == "completed"
                and {prefix+key for prefix in ("", "raw:") for key in ("top_20", "bottom_20", "quintile_2", "quintile_3", "quintile_4")}.issubset(set(frame.portfolio))
                and not frame.duplicated(["portfolio", "week_id"]).any())
    except (OSError, ValueError, KeyError):
        return False


def run_report_backtests(*, factor_name: str, factor_frame: pd.DataFrame,
                         raw_factor_frame: pd.DataFrame, market_data: pd.DataFrame, context: MarketContext,
                         output_dir: Path, initial_capital: float = 1_000_000.0,
                         minimum_coverage: float = 0.85, lot_size: int = 100,
                         resume: bool = False) -> dict[str, Any]:
    """双版本核心五分组及中性化细节组合均通过同一精细账户模拟器。"""
    signature = report_return_signature(context, initial_capital, minimum_coverage, lot_size)
    source_hash = hashlib.sha256(pd.util.hash_pandas_object(factor_frame, index=True).values.tobytes()).hexdigest()
    signature["neutralized_factor_hash"] = source_hash
    signature["raw_factor_hash"] = hashlib.sha256(
        pd.util.hash_pandas_object(raw_factor_frame,index=True).values.tobytes()).hexdigest()
    if initial_capital <= 0 or not 0 < minimum_coverage <= 1 or lot_size <= 0:
        raise ValueError("本金、覆盖率或整手单位无效")
    dates = pd.DatetimeIndex(p.first_trade for p in context.periods)
    cap = market_data["total_mv"].unstack("symbol").reindex(index=dates,columns=context.symbols)
    industry = market_data["industry_sw_1"].unstack("symbol").reindex(index=dates,columns=context.symbols)
    signature["size_industry_sha256"]=hashlib.sha256(
        pd.util.hash_pandas_object(cap,index=True).values.tobytes()+
        pd.util.hash_pandas_object(industry,index=True).values.tobytes()).hexdigest()
    if resume and report_returns_ready(output_dir, signature):
        return {"factor":factor_name,"status":"already_completed"}
    member_cap = cap.where(context.candidate_mask)
    cap_rank = member_cap.rank(axis=1,pct=True,method="first")
    masks = {"size_small":cap_rank.le(1/3).to_numpy(),
             "size_middle":(cap_rank.gt(1/3)&cap_rank.le(2/3)).to_numpy(),
             "size_large":cap_rank.gt(2/3).to_numpy()}
    industries = sorted(str(v) for v in market_data["industry_sw_1"].dropna().unique() if str(v).strip())
    for name in industries:
        masks["industry:"+name] = industry.eq(name).fillna(False).to_numpy(dtype=bool)
    frame = factor_frame.sort_values("signal_date").copy()
    values, available, signals, _ = _load_factor_snapshots(Path('.'),context,frame=frame)
    raw_snapshots = _load_factor_snapshots(Path('.'),context,frame=raw_factor_frame)[:3]
    lag_snapshots = {}
    for lag in range(1,4):
        shifted = frame.copy()
        columns = list(shifted.columns[2:])
        shifted[columns] = shifted[columns].shift(lag)
        # 行的可用时点仍决定何时发布；审计信号日指向实际使用的历史观测。
        shifted["signal_date"] = shifted.signal_date.shift(lag)
        lag_snapshots[lag] = _load_factor_snapshots(Path('.'),context,frame=shifted)[:3]
    specs = [("top_20","higher",.2,.3,None,None,0),
             ("bottom_20","lower",.2,.3,None,None,0)]
    specs += [(f"quintile_{g}","lower",.2,.3,g,None,0) for g in (2,3,4)]
    specs += [(f"{side}_{pct}",direction,pct/100,(pct+10)/100,None,None,0)
              for pct in (10,30) for side,direction in (("top","higher"),("bottom","lower"))]
    specs += [(f"lag_{lag}:{side}_20",direction,.2,.3,None,None,lag)
              for lag in range(1,4) for side,direction in (("top","higher"),("bottom","lower"))]
    specs += [(key+":"+side+"_20",direction,.2,.3,None,mask,0)
              for key,mask in masks.items() for side,direction in (("top","higher"),("bottom","lower"))]
    # 原始值只计算核心指标需要的五组，不生成原始行业、市值、滞后或年度细节。
    specs += [("raw:"+key,direction,buy,hold,quintile,mask,lag)
              for key,direction,buy,hold,quintile,mask,lag in specs[:5]]
    parts, summaries, unavailable = [], {}, {}
    for key,direction,buy,hold,quintile,mask,lag in specs:
        selected_context = context if mask is None else replace(context,candidate_mask=context.candidate_mask&mask)
        version = "raw" if key.startswith("raw:") else "neutralization"
        fv,ua,us = raw_snapshots if version=="raw" else ((values,available,signals) if not lag else lag_snapshots[lag])
        try:
            rows,summary = _simulate_direction(
                factor_name=factor_name,factor_column=factor_name+"_"+version,direction=direction,
                factor_values=fv,used_available=ua,used_signal=us,context=selected_context,
                initial_capital=initial_capital,minimum_coverage=minimum_coverage,lot_size=lot_size,
                buy_fraction=buy,hold_fraction=hold,quintile=quintile)
        except ValueError as error:
            # 仅真实无有效组合的细分层允许留空；全池五分组不完整必须失败。
            if key.removeprefix("raw:") in {"top_20","bottom_20","quintile_2","quintile_3","quintile_4"}:
                raise
            if "整个请求区间都未达到最低因子覆盖率" not in str(error):
                raise
            unavailable[key] = str(error)
            continue
        table = pd.DataFrame(rows)
        if len(table)!=len(context.periods):
            # 部分行业可晚于2020年出现，保留实际有效起点且在报告披露，不伪造前期收益。
            summary["partial_coverage"] = True
        table.insert(0,"portfolio",key)
        parts.append(table)
        summaries[key]=summary
    combined = pd.concat(parts,ignore_index=True)
    for column in ("week_first_trade","week_last_trade"):
        combined[column]=pd.to_datetime(combined[column])
    out = Path(output_dir);out.parent.mkdir(parents=True,exist_ok=True)
    temporary = out.parent/f'.{out.name}.report.{uuid.uuid4().hex}.tmp'
    temporary.mkdir()
    try:
        write_output_parquet(combined,temporary/"report_portfolios.parquet")
        baseline = combined.loc[combined.portfolio.isin(["top_20","bottom_20"])].copy()
        week_count = baseline.week_id.nunique()
        for version,prefix in (("neutralization",""),("raw","raw:")):
            version_baseline=combined.loc[combined.portfolio.isin([prefix+"top_20",prefix+"bottom_20"])].copy()
            version_baseline["direction"]=version_baseline.portfolio.map({prefix+"top_20":"higher",prefix+"bottom_20":"lower"})
            version_compact=version_baseline.pivot(index=["week_id","week_first_trade","week_last_trade"],columns="direction",values="weekly_return").reset_index()
            write_output_parquet(version_compact[["week_id","week_first_trade","week_last_trade","higher","lower"]],temporary/(version+".parquet"))
        benchmark = baseline.drop_duplicates("week_id").set_index("week_id").benchmark_return.to_dict()
        common={"status":"completed","engine_version":ENGINE_VERSION,"factor_name":factor_name,
                "factor_versions":["raw","neutralization"],"requested_start":str(context.requested_start.date()),
                "requested_end":str(context.requested_end.date()),"source_paths":context.source_paths,
                "engine_sha256":signature["engine_sha256"],"initial_capital":initial_capital,
                "minimum_factor_coverage":minimum_coverage,"lot_size":lot_size,
                "fees":{"commission_rate":.0003,"minimum_commission":5.0,"transfer_fee_rate":.00001,
                        "stamp_tax_rate_on_sell":.001},"slippage_rate":0.0,
                "execution_policy":"first exchange trading day close; weekly closing valuation",
                "quintile_policy":"ascending disjoint quintiles; end groups exactly match Top20/Bottom20; middle hold band extends by 5 percentage points each side",
                "tail_policy":"buy inside selected fraction; existing holdings retained inside fraction+10 percentage points",
                "benchmark_weekly_returns":{v:benchmark for v in ("raw","neutralization")},
                "summary":{v:[summaries[p+"top_20"],summaries[p+"bottom_20"]]
                           for v,p in (("neutralization",""),("raw","raw:"))}}
        _atomic_write_json(common,temporary/"metadata.json")
        _atomic_write_json({**common,"signature":signature,"portfolio_summaries":summaries,
                            "unavailable_portfolios":unavailable},temporary/"report_return_metadata.json")
        out.mkdir(exist_ok=True)
        for file in temporary.iterdir():os.replace(file,out/file.name)
    finally:
        shutil.rmtree(temporary,ignore_errors=True)
    return {"factor":factor_name,"status":"completed","weeks_higher":week_count,
            "weeks_lower":week_count,"return_higher":summaries["top_20"]["total_return"],
            "return_lower":summaries["bottom_20"]["total_return"],"portfolio_count":len(summaries)}
