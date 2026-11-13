"""因子自有 Parquet 输入契约：动态月分区、财报可用时点和分钟复权。"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd
from dataloader import (resolve_project_path, resolve_data_path, read_constituent_table,
                        read_parquet_table, read_chip_distribution_table, CHIP_AGGREGATIONS,
                        normalize_dates as _dates)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ParquetInput:
    """路径及业务字段由各因子声明；None 表示尚未提供的数据源。

    expression 只支持列名、数字、四则运算及 sum_available/coalesce。
    announcement_columns 声明按优先顺序取实际公告日，不使用报告期末作可用日。
    adjustment 为分钟原始价格对应的日频复权因子来源。
    """
    path: str | None
    field: str | None
    date_column: str = "trade_date"
    symbol_column: str | None = "ts_code"
    membership: bool = False
    pending: bool = False
    expression: str | None = None
    announcement_columns: tuple[str, ...] = ()
    report_period_column: str = "end_date"
    filters: tuple[tuple[str, str], ...] = ()
    adjustment: ParquetInput | None = None
    aggregation: str | None = None


def validate_sources(sources: Mapping[str, ParquetInput]) -> None:
    pending = [name for name, source in sources.items()
               if source.pending or not source.path or not source.field]
    if pending:
        raise ValueError("输入来源尚未配置（指数或运行层状态数据需后续补充）: " + ", ".join(pending))
    if not sources:
        raise ValueError("因子未声明输入字段")
    for name, source in sources.items():
        resolve_data_path(source.path)
        if source.aggregation:
            if (source.aggregation not in CHIP_AGGREGATIONS or name != source.aggregation
                    or source.field != 'chip_price' or source.date_column != 'trade_date'
                    or source.symbol_column != 'ts_code' or source.expression
                    or source.announcement_columns or source.filters or source.adjustment):
                raise ValueError(f'不支持的筹码聚合输入: {name}')
        if not source.membership and not source.expression and not source.aggregation and name != source.field:
            raise ValueError(f"直接输入必须使用Parquet真实字段名: {name!r} != {source.field!r}")
        if source.adjustment:
            validate_sources({source.adjustment.field: source.adjustment})


def _expression_columns(source: ParquetInput) -> list[str]:
    if source.aggregation:
        return ['chip_price', 'chip_percent']
    if not source.expression:
        return [source.field]
    tree = ast.parse(source.expression, mode="eval")
    return sorted({node.id for node in ast.walk(tree)
                   if isinstance(node, ast.Name) and node.id not in {"sum_available", "coalesce"}})


def _value(frame: pd.DataFrame, source: ParquetInput) -> pd.Series:
    if source.aggregation:
        return frame[source.aggregation]
    if not source.expression:
        return frame[source.field]
    def calculate(node):
        if isinstance(node, ast.Expression): return calculate(node.body)
        if isinstance(node, ast.Name): return frame[node.id]
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            x = calculate(node.operand)
            return -x if isinstance(node.op, ast.USub) else x
        if isinstance(node, ast.BinOp):
            a, b = calculate(node.left), calculate(node.right)
            if isinstance(node.op, ast.Add): return a + b
            if isinstance(node.op, ast.Sub): return a - b
            if isinstance(node.op, ast.Mult): return a * b
            if isinstance(node.op, ast.Div):
                return a / (b.where(b != 0) if isinstance(b, pd.Series) else (b or np.nan))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            args = [calculate(a) for a in node.args]
            if node.func.id == "sum_available" and args:
                return pd.concat(args, axis=1).sum(axis=1, min_count=1)
            if node.func.id == "coalesce" and args:
                result = args[0]
                for item in args[1:]: result = result.combine_first(item)
                return result
        raise ValueError(f"不支持的输入表达式: {source.expression}")
    return calculate(ast.parse(source.expression, mode="eval"))


def _read_table(source: ParquetInput, *, start=None, end=None, symbols=None,
                extra_columns=()) -> pd.DataFrame:
    path = resolve_data_path(source.path)
    if source.aggregation:
        return read_chip_distribution_table(path, start=start, end=end, symbols=symbols)
    keys = [source.date_column] + ([source.symbol_column] if source.symbol_column else [])
    columns = list(dict.fromkeys(keys + _expression_columns(source)
                + list(source.announcement_columns)
                + ([source.report_period_column] if source.announcement_columns else [])
                + [k for k, _ in source.filters] + list(extra_columns)))
    frame = read_parquet_table(path, columns, date_column=source.date_column,
                               symbol_column=source.symbol_column,
                               start=None if source.announcement_columns else start,
                               end=None if source.announcement_columns else end, symbols=symbols)
    for key, expected in source.filters:
        frame = frame.loc[frame[key].astype("string").str.replace(r"\.0$", "", regex=True).eq(expected)]
    if source.symbol_column:
        frame[source.symbol_column] = frame[source.symbol_column].astype("string")
        if symbols is not None: frame = frame.loc[frame[source.symbol_column].isin([str(s) for s in symbols])].copy()
    for key in dict.fromkeys([source.date_column, *source.announcement_columns,
                              *([source.report_period_column] if source.announcement_columns else [])]):
        frame[key] = _dates(frame[key])
    if source.announcement_columns:
        available = frame[source.announcement_columns[0]]
        for key in source.announcement_columns[1:]: available = available.combine_first(frame[key])
        frame["_available"] = available
        if frame[["_available", source.report_period_column, source.symbol_column]].isna().any().any():
            raise ValueError(f"财报缺少公告日、报告期或股票代码: {path}")
        if end is not None: frame = frame.loc[frame._available < pd.Timestamp(end).normalize()+pd.Timedelta(days=1)]
    else:
        if frame[keys].isna().any().any(): raise ValueError(f"输入存在空日期/股票键: {path}")
        if start is not None: frame = frame.loc[frame[source.date_column] >= pd.Timestamp(start)]
        if end is not None: frame = frame.loc[frame[source.date_column] < pd.Timestamp(end).normalize()+pd.Timedelta(days=1)]
        if frame.duplicated(keys).any(): raise ValueError(f"输入存在重复日期/股票键: {path}")
    return frame


def _financial_series(frame: pd.DataFrame, source: ParquetInput,
                      anchor: pd.MultiIndex, logical: str) -> pd.Series:
    frame = frame.copy()
    frame[logical] = _value(frame, source)
    keys = [source.symbol_column, "_available", source.report_period_column]
    # 完全相同的计算记录可折叠，冲突的同日同报告期数值不猜测版本优先级。
    frame = frame[keys + [logical]].drop_duplicates()
    conflicts = frame.duplicated(keys, keep=False)
    if conflicts.any():
        # 没有可靠版本顺序时保留不确定性；该科目在此生效版本为缺失，
        # 后续已公告修订仍可恢复，不能任意选值或让整个股票池计算中止。
        missing = pd.NaT if pd.api.types.is_datetime64_any_dtype(frame[logical]) else np.nan
        frame.loc[conflicts, logical] = missing
        frame = frame.drop_duplicates(keys)
    pieces = []
    for symbol, target in anchor.to_frame(index=False).groupby("symbol", sort=False):
        records = frame.loc[frame[source.symbol_column].eq(symbol)].sort_values(
            ["_available", source.report_period_column])
        if records.empty:
            pieces.append(pd.Series(np.nan, index=pd.MultiIndex.from_frame(target), name=logical))
            continue
        # 迟到的旧报告不能覆盖当时已知的较新报告；同一报告期后续更正仅向后生效。
        records = records.loc[records[source.report_period_column].eq(records[source.report_period_column].cummax())]
        records = records.drop_duplicates("_available", keep="last")
        joined = pd.merge_asof(target.sort_values("date"), records[["_available", logical]],
                               left_on="date", right_on="_available", direction="backward",
                               allow_exact_matches=False)
        pieces.append(joined.set_index(["date", "symbol"])[logical])
    return pd.concat(pieces).reindex(anchor) if pieces else pd.Series(index=anchor, dtype=float, name=logical)


def read_inputs(sources: Mapping[str, ParquetInput], *, start=None, end=None,
                symbols=None) -> pd.DataFrame:
    """动态读取分区；日频键锚定股票行情，财报从公告后的交易日开始可用。"""
    validate_sources(sources)
    tables = {}
    table_indexes = {}
    def table_key(source):
        return (source.path, source.date_column, source.symbol_column,
                source.announcement_columns, source.report_period_column, source.filters,
                bool(source.aggregation))
    requested_columns = {}
    for source in sources.values():
        if source.membership:
            continue
        for item in (source, source.adjustment):
            if item is not None:
                requested_columns.setdefault(table_key(item), set()).update(_expression_columns(item))
    def table(source):
        key = table_key(source)
        if key not in tables:
            tables[key] = _read_table(source, start=start, end=end, symbols=symbols,
                                      extra_columns=sorted(requested_columns[key]))
        return tables[key]
    stock, broadcasts, financial, states = [], [], [], []
    for logical, source in sources.items():
        if source.membership:
            continue
        frame = table(source)
        if source.announcement_columns:
            financial.append((logical, source, frame)); continue
        keys = [source.date_column] + ([source.symbol_column] if source.symbol_column else [])
        values = _value(frame, source).copy()
        if source.adjustment:
            adjust = table(source.adjustment)
            a = source.adjustment
            series = _value(adjust, a)
            series.index = pd.MultiIndex.from_frame(adjust[[a.date_column, a.symbol_column]])
            aligned = pd.MultiIndex.from_arrays([frame[source.date_column].dt.normalize(), frame[source.symbol_column]])
            multiplier = series.reindex(aligned).to_numpy()
            if np.any(pd.notna(values) & ~np.isfinite(multiplier)):
                raise ValueError(f"分钟价格缺少同日复权因子: {source.path}")
            values = values * multiplier
        # Fields projected from the same physical table have identical keys.
        # Reuse the index instead of rebuilding/factorizing millions of minute
        # keys for every OHLCV column before concatenation.
        key = table_key(source)
        if key not in table_indexes:
            index = pd.MultiIndex.from_frame(frame[keys]) if source.symbol_column else pd.DatetimeIndex(frame[source.date_column])
            index.names = ["date", "symbol"] if source.symbol_column else ["date"]
            table_indexes[key] = index
        index = table_indexes[key]
        series = pd.Series(values.to_numpy(), index=index, name=logical)
        if logical in {"is_st", "is_suspended"} and source.symbol_column:
            states.append(series)
        else:
            (stock if source.symbol_column else broadcasts).append(series)
    if not stock: raise ValueError("至少需要一张日频或分钟股票行情表作为日期/股票锚点")
    if all(series.index is stock[0].index for series in stock):
        # Avoid consolidating all projected OHLCV columns into another large
        # allocation.  Independent tables still take the normal outer join.
        data = pd.DataFrame({series.name:series.to_numpy(copy=False) for series in stock},
                            index=stock[0].index,copy=False)
    else:
        data = pd.concat(stock, axis=1)
    if not data.index.is_monotonic_increasing:data=data.sort_index()
    stock_dates = pd.DatetimeIndex(data.index.get_level_values("date").unique()).normalize()
    market_calendar = next((pd.DatetimeIndex(series.index).normalize().unique()
                            for series in broadcasts if series.name == "benchmark_close"), None)
    if market_calendar is not None:
        # 日频大表为多来源日期并集；只在指数交易日计算，不改动原始数据。
        data = data.loc[data.index.get_level_values("date").normalize().isin(market_calendar)]
    # 状态是行情的辅助字段，不生成没有行情的股票/日期行；空值按用户口径视为正常。
    for series in states:
        data[series.name] = series.reindex(data.index).astype("boolean").fillna(False).astype(bool)
    for logical, source, frame in financial:
        data[logical] = _financial_series(frame, source, data.index, logical)
    for series in broadcasts:
        data[series.name] = series.reindex(data.index.get_level_values("date")).to_numpy()
    for logical, source in sources.items():
        if not source.membership:
            continue
        members = read_constituent_table(resolve_project_path(source.path))
        if market_calendar is not None and len(stock_dates):
            expected = pd.DatetimeIndex(members.date)
            expected = expected[(expected >= stock_dates.min()) & (expected <= stock_dates.max())]
            absent = expected.difference(market_calendar)
            if len(absent):
                raise ValueError(f"指数行情缺少成分股交易日: {absent[:5].tolist()}")
        dates = pd.DatetimeIndex(data.index.get_level_values("date")).normalize()
        missing = dates.unique().difference(pd.DatetimeIndex(members.date))
        if len(missing):
            raise ValueError(f"逐日成分股缺少行情日期: {missing[:5].tolist()}")
        expanded = members.assign(symbol=members.tickers.str.split(",")).explode("symbol")
        expanded["symbol"] = expanded.symbol.str.strip()
        member_keys = pd.MultiIndex.from_frame(expanded[["date", "symbol"]])
        keys = pd.MultiIndex.from_arrays([dates, data.index.get_level_values("symbol")])
        data[logical] = keys.isin(member_keys)
    return data


def boolean_values(values: pd.Series) -> pd.Series:
    """严格识别已对齐的布尔字段；交易状态空值在输入合并时按正常处理。"""
    normalized = values.astype(str).str.lower()
    known = normalized.isin({"true", "false", "1", "0", "1.0", "0.0", "t", "f", "y", "n", "yes", "no"})
    if not known.all():
        raise ValueError(f"状态字段 {values.name} 包含缺失或未知布尔值")
    return normalized.isin({"true", "1", "1.0", "t", "y", "yes"})


def fixed_factor(name: str, defaults: dict):
    """绑定因子身份；禁止通过改窗口或操作把一个文件变成另一个因子。"""
    def decorate(cls):
        original_init = cls.__init__
        @wraps(original_init)
        def initialize(self, **kwargs):
            for key in ("operation", "window", "lookback", "period", "exclude_recent", "shift_days"):
                if key in kwargs and kwargs[key] != defaults.get(key):
                    raise ValueError(f"{name} 的 {key} 已固定为 {defaults.get(key)!r}")
            params = {**defaults, **kwargs}
            original_init(self, **params)
            self.name = name
        cls.__init__ = initialize
        cls.name = name
        return cls
    return decorate


class FactorDataLoader:
    """合并因子公式输入与运行层输入，并构建评估所需的数据。"""

    def __init__(self, factor=None, *, runtime_inputs, universe, start=None, end=None, symbols=None,
                 warmup_days=0, context_only=False):
        self.factor = factor
        self.start, self.end, self.symbols = start, end, symbols
        self.warmup_days = warmup_days
        self.universe = universe
        self.sources = dict(runtime_inputs)
        if not context_only:
            if factor is None:
                raise ValueError("计算因子时必须提供因子对象")
            for name, source in getattr(factor, "INPUTS", {}).items():
                if (getattr(factor, "PRESERVE_REPORT_HISTORY", False)
                        and source.announcement_columns):
                    # 新公开财务因子自行读取完整报告期/修订快照，不能先压成最新值。
                    continue
                if name in self.sources and self.sources[name] != source:
                    raise ValueError(f"公式与运行层的同名输入来源冲突: {name}")
                self.sources[name] = source
        self.data = self.benchmark = self.constituents = self.security_status = pd.DataFrame()
        self.trading_calendar = self.history_calendar = pd.DatetimeIndex([])

    def load_history(self, *, start, end):
        """为需要独立训练历史的因子提供全股票数据，状态来源由运行层配置。"""
        return read_inputs(self.sources, start=start, end=end)

    def load_all(self, apply_universe_filters=True):
        read_start = None
        if self.start is not None and getattr(self.factor, 'BOUNDED_HISTORY', False):
            # 自研日线均只依赖已存日频值；按实际指数交易日预读，不改变旧因子的历史加载。
            calendar_source = self.sources['benchmark_close']
            calendar_frame = _read_table(calendar_source, end=self.end)
            history = pd.DatetimeIndex(calendar_frame[calendar_source.date_column].unique()).sort_values()
            if len(history):
                position = max(0, history.searchsorted(pd.Timestamp(self.start)) - self.warmup_days)
                read_start = history[min(position, len(history)-1)]
        data = read_inputs(self.sources, start=read_start, end=self.end, symbols=self.symbols)
        self.constituents = boolean_values(data["is_member"]).unstack("symbol").astype("boolean").fillna(False).astype(bool)
        calendar = pd.DatetimeIndex(data.index.get_level_values("date").unique()).sort_values()
        if self.start is not None:
            position = max(0, calendar.searchsorted(pd.Timestamp(self.start)) - self.warmup_days)
            calendar = calendar[position:]
            data = data.loc[data.index.get_level_values("date").isin(calendar)]
        self.history_calendar = calendar
        self.trading_calendar = calendar if self.start is None else calendar[calendar >= pd.Timestamp(self.start)]
        # 正式筛选只看ST与全天停牌；状态缺失按正常处理。
        excluded = boolean_values(data["is_st"]) | boolean_values(data["is_suspended"])
        # 状态表缺行已补False；没有行情行的样本不输出信号。
        self.security_status = excluded.unstack("symbol").astype("boolean").fillna(True).astype(bool)
        benchmark = data["benchmark_close"].groupby(level="date")
        if (benchmark.nunique(dropna=True) > 1).any():
            raise ValueError("同日 benchmark_close 在不同股票间不一致")
        self.benchmark = benchmark.first().to_frame(self.universe.upper())
        if apply_universe_filters:
            eligible = boolean_values(data["is_member"]) & ~excluded
            data = data.loc[eligible]
        self.data = data
        return data

    def filter_signals_to_universe(self, signals: pd.DataFrame) -> pd.DataFrame:
        """仅在信号输出日应用回测区间、成分股、ST 和停牌过滤。"""
        if signals.empty:
            return signals
        filtered = signals.copy()
        if not isinstance(filtered.index, pd.DatetimeIndex):
            filtered.index = pd.to_datetime(filtered.index)
        filtered = filtered.sort_index()
        if self.start is not None:
            filtered = filtered.loc[filtered.index >= pd.Timestamp(self.start)]
        if self.end is not None:
            filtered = filtered.loc[filtered.index <= pd.Timestamp(self.end)]

        eligible = pd.DataFrame(True, index=filtered.index, columns=filtered.columns)
        if not self.constituents.empty:
            eligible &= self.constituents.reindex(
                index=filtered.index,
                columns=filtered.columns,
                fill_value=False,
            )
        if not self.security_status.empty:
            excluded = self.security_status.reindex(
                index=filtered.index,
                columns=filtered.columns,
                fill_value=False,
            )
            eligible &= ~excluded
        filtered = filtered.where(eligible)
        filtered.index.name = signals.index.name or "date"
        filtered.columns.name = signals.columns.name or "symbol"
        return filtered

