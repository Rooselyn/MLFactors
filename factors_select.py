"""统一月度因子筛选入口。

通过 --selection-mode ic 按信息系数筛选，通过
--selection-mode return 按完整自然周复利净收益筛选。公共因子读取、
最终因子拼接、报告生成和收益 final 重建均内置于本文件。
"""

from __future__ import annotations

from dataloader import read_constituent_table

from dataloader import portable_path, portable_payload, portable_frame, resolve_project_path
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import shutil
import sys
import traceback
from typing import Any
import uuid

import numpy as np
import pandas as pd
from tqdm import tqdm

from factors.registry import CATEGORY_NAMES, load_categories, load_factor_configs
import run as legacy
from factors.inputs import FactorDataLoader


from dataloader import read_factor_output, read_weekly_output, write_output_parquet, daily_member_mask, fill_member_values


def _factor_symbols(directory):
    import pyarrow.parquet as pq
    return list(pq.read_schema(Path(directory) / "raw.parquet").names[2:])


def _read_factor_stock(directory, name, symbol):
    frames = []
    for version in ("raw", "neutralization"):
        path = Path(directory) / f"{version}.parquet"
        if symbol not in _factor_symbols(directory):
            return None
        frame = pd.read_parquet(path, columns=["signal_date", "available_date", symbol])
        frame = frame.rename(columns={symbol: f"{name}_{version}"}).set_index(["signal_date", "available_date"])
        frames.append(frame)
    return pd.concat(frames, axis=1).reset_index()


def _consolidate_factor_staging(directory, name):
    """合并选因子过程中的逐股票Parquet暂存，最终仅保留两个版本的宽表。"""
    directory = Path(directory)
    staging = directory / "factors"
    if not staging.is_dir():
        return
    pieces = {v: [] for v in ("raw", "neutralization")}
    for path in sorted(staging.glob("*.parquet")):
        frame = pd.read_parquet(path)
        for key in ("signal_date", "available_date"):
            frame[key] = pd.to_datetime(frame[key])
        for version in pieces:
            column = f"{name}_{version}"
            pieces[version].append(frame.set_index(["signal_date", "available_date"])[column].rename(path.stem))
    for version, series in pieces.items():
        if not series:
            raise ValueError(f"无因子暂存数据: {directory}")
        frame = pd.concat(series, axis=1).sort_index().reset_index()
        if frame.signal_date.duplicated().any():
            raise ValueError("同一信号日不同股票的可用日期不一致")
        write_output_parquet(frame, directory / f"{version}.parquet")
    shutil.rmtree(staging)


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_FIRST_MONTH = "2019-12"
DEFAULT_FINAL_MONTH = "2026-05"
DEFAULT_SOURCE_ROOT = legacy.DEFAULT_OUTPUT_ROOT
DEFAULT_IC_ROOT = legacy.DEFAULT_IC_OUTPUT_ROOT
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "outputs_new" / "zz500"
DEFAULT_WORKERS = 50
ML_FACTOR_NAME = "momentum_ml_252n20d"

_SOURCE_ROOT = DEFAULT_SOURCE_ROOT
_IC_ROOT = DEFAULT_IC_ROOT
_IC_VERSION = "neutralization"
_SELECTION_DATA_DIR = legacy.DEFAULT_DATA_DIR
_SELECTION_CONSTITUENTS = legacy.WEEKLY_CONSTITUENTS
_SELECTION_CONSTITUENT_INDEX = "000905.SH"


def _selection_members():
    key = (str(_SELECTION_CONSTITUENTS), _SELECTION_CONSTITUENTS.stat().st_mtime_ns)
    if getattr(_selection_members, "key", None) != key:
        frame = read_constituent_table(_SELECTION_CONSTITUENTS)
        expanded = frame.assign(symbol=frame.tickers.str.split(",")).explode("symbol")
        expanded["symbol"] = expanded.symbol.str.strip()
        _selection_members.value = expanded.assign(member=True).pivot(
            index="date", columns="symbol", values="member").astype("boolean").fillna(False).astype(bool)
        _selection_members.key = key
    return _selection_members.value


def _member_rows(frame, symbol):
    values = pd.DataFrame(index=pd.DatetimeIndex(frame["signal_date"]), columns=[symbol])
    return daily_member_mask(values, _selection_members())[symbol].to_numpy()


def _fill_selected_series(frame, symbol, values, initial_value=0.0):
    matrix = pd.DataFrame({symbol: values.to_numpy()}, index=pd.DatetimeIndex(frame["signal_date"]))
    return fill_member_values(matrix, _selection_members(), initial_value=initial_value)[symbol].to_numpy()


def _run_parallel_collect(
    function: Any,
    items: list[Any],
    workers: int,
    description: str,
) -> list[dict[str, Any]]:
    """用 fork 进程池执行因子任务，并统一报告失败。"""
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    context = mp.get_context("fork")
    with ProcessPoolExecutor(max_workers=workers, mp_context=context) as executor:
        futures = {executor.submit(function, item): item for item in items}
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc=description,
            unit="factor",
        ):
            result = future.result()
            results.append(result)
            if result["status"] == "failed":
                failures.append(result)
                tqdm.write(
                    f"FAILED {result['factor']}\n{result.get('traceback', '')}"
                )
    if failures:
        raise RuntimeError(f"{description}失败: {len(failures)}")
    return results


def _assert_source_is_read_only_scope(source_root: Path, output_root: Path) -> None:
    """禁止输出目录等于或位于只读源目录内部。"""
    source = source_root.resolve()
    output = output_root.resolve()
    if source == output or source in output.parents or output in source.parents:
        raise ValueError(
            "输出目录与只读源目录不能相同，也不能互为父子目录: "
            f"source={source}, output={output}"
        )
    if not source.is_dir():
        raise FileNotFoundError(f"既有因子值目录不存在: {source}")


def _load_configs(
    expansion_config_path: Path,
    base_config_path: Path,
) -> dict[str, dict[str, Any]]:
    """加载包含机器学习动量及保留扩展因子的正式配置。"""
    configs = load_factor_configs(base_config_path, expansion_config_path)
    legacy._validate_full_config(configs)
    if ML_FACTOR_NAME not in configs:
        raise ValueError(f"全量配置缺少 {ML_FACTOR_NAME}")
    return configs


def _validate_source_factor_dirs(source_root: Path, factor_names: list[str]) -> None:
    missing = [n for n in factor_names if not all((source_root / n / f"{v}.parquet").is_file() for v in ("raw", "neutralization"))]
    if missing:
        raise FileNotFoundError(f"因子Parquet缺失: {missing[:10]}")


def _validate_ic_files(ic_root: Path, factor_names: list[str]) -> None:
    """校验每个正式因子都有可直接读取的逐日 IC 文件。"""
    if not ic_root.is_dir():
        raise FileNotFoundError(f"逐日 IC 目录不存在: {ic_root}")
    missing = [name for name in factor_names if not (ic_root / name / f"{_IC_VERSION}.parquet").is_file()]
    if missing:
        raise FileNotFoundError(
            f"逐日 IC 目录中有 {len(missing)} 个因子缺少 Parquet: {missing[:10]}"
        )


def _load_saved_ic_series(name: str) -> pd.Series:
    """读取 run.py 已保存的 5 日未来收益口径逐日 Rank IC。"""
    path = _IC_ROOT / name / f"{_IC_VERSION}.parquet"
    column = f"IC_{_IC_VERSION}"
    try:
        frame = pd.read_parquet(path, columns=["signal_date", column])
    except ValueError as error:
        raise ValueError(f"{path} 缺少字段 signal_date、{column}") from error
    if frame.empty:
        raise ValueError(f"逐日 IC 文件为空: {path}")
    if frame["signal_date"].isna().any():
        raise ValueError(f"逐日 IC 存在无效日期: {path}")
    if frame["signal_date"].duplicated().any():
        raise ValueError(f"逐日 IC 存在重复日期: {path}")
    series = pd.Series(
        pd.to_numeric(frame[column], errors="coerce").to_numpy(dtype="float64"),
        index=pd.DatetimeIndex(frame["signal_date"], name="date"),
        name="IC",
    ).sort_index()
    calendar = pd.DatetimeIndex(legacy._PIPELINE_DATES, name="date").sort_values().unique()
    if calendar.empty:
        raise ValueError("逐日 IC 对齐所需的交易日历为空")
    required_start = min(_WINDOW_IC_STARTS) if _WINDOW_IC_STARTS else calendar[0]
    required_end = max(_WINDOW_FACTOR_ENDS) if _WINDOW_FACTOR_ENDS else calendar[-1]
    if series.index[0] > required_start or series.index[-1] < required_end:
        raise ValueError(
            f"{name} 逐日 IC 覆盖不足: {series.index[0]:%Y-%m-%d} 至 "
            f"{series.index[-1]:%Y-%m-%d}，要求 {required_start:%Y-%m-%d} 至 "
            f"{required_end:%Y-%m-%d}"
        )
    return series.reindex(calendar)


def _load_categories(
    configs: dict[str, dict[str, Any]],
    factor_names: set[str],
) -> tuple[list[str], dict[str, str]]:
    return load_categories(configs, factor_names)


def _read_trading_calendar(start: str, final_month: str) -> pd.DatetimeIndex:
    """读取Parquet成分股交易日历，并截取请求区间。"""
    calendar = _load_full_calendar(_SELECTION_CONSTITUENTS)
    final_period = pd.Period(final_month, freq="M")
    calendar = calendar[
        (calendar >= pd.Timestamp(start))
        & (calendar <= final_period.end_time.normalize())
    ]
    if calendar.empty:
        raise ValueError(f"交易日历在 {start} 至 {final_month} 范围内为空")
    return calendar


def _load_source_factor_series(name: str) -> pd.Series:
    frame = read_factor_output(_SOURCE_ROOT / name, _IC_VERSION)
    frame = frame.loc[frame.signal_date.between(legacy._PIPELINE_DATES[0], legacy._PIPELINE_DATES[-1])]
    if frame.empty:
        raise ValueError(f"{name} 在总回测区间没有因子值")
    return frame.drop(columns="available_date").set_index("signal_date").rename_axis(index="date", columns="symbol").stack(dropna=False).rename("factor")


def _select_category_winners(
    ic_frame: pd.DataFrame,
    category_names: list[str],
    factor_to_category: dict[str, str],
) -> dict[str, tuple[str, float]]:
    """每类按 |IC_mean| 降序、因子名升序确定唯一胜出因子。"""
    values = ic_frame.copy()
    values["category"] = values["factor_name"].map(factor_to_category)
    values["IC_mean"] = pd.to_numeric(values["IC_mean"], errors="coerce")
    values = values[np.isfinite(values["IC_mean"])]
    winners: dict[str, tuple[str, float]] = {}
    for category_name in category_names:
        candidates = values.loc[values["category"].eq(category_name)].copy()
        if candidates.empty:
            raise ValueError(f"类别 {category_name} 没有可用的 IC_mean")
        candidates["abs_IC_mean"] = candidates["IC_mean"].abs()
        winner = candidates.sort_values(
            ["abs_IC_mean", "factor_name"],
            ascending=[False, True],
            kind="mergesort",
        ).iloc[0]
        winners[category_name] = (
            str(winner["factor_name"]),
            float(winner["IC_mean"]),
        )
    return winners


def _materialize_filled_factor(task: tuple[str, str, str, str]) -> dict[str, Any]:
    name, start_text, endpoint_text, root_text = task
    temporary = Path(root_text) / f".{name}.{uuid.uuid4().hex}.tmp"
    try:
        count = 0
        for version in ("raw", "neutralization"):
            frame = read_factor_output(_SOURCE_ROOT / name, version, start=start_text, end=endpoint_text)
            if frame.empty:
                raise ValueError(f"{name} 在目标窗口无因子值")
            values = frame.iloc[:, 2:].replace([np.inf, -np.inf], np.nan)
            values.index = pd.DatetimeIndex(frame.signal_date)
            count += int((values.isna() & daily_member_mask(values, _selection_members())).sum().sum())
            frame[values.columns] = fill_member_values(values, _selection_members()).to_numpy()
            write_output_parquet(frame, temporary / f"{version}.parquet")
        destination = Path(root_text) / name
        if destination.exists(): shutil.rmtree(destination)
        temporary.replace(destination)
        return _result(name, "completed", files=2, cells_filled=count)
    except Exception:
        if temporary.exists(): shutil.rmtree(temporary)
        return _result(name, "failed", traceback=traceback.format_exc())


def _prepare_window_directory(window_root: Path, resume: bool) -> None:
    if not window_root.exists():
        window_root.mkdir(parents=True)
        return
    if not any(window_root.iterdir()):
        return
    if not resume:
        raise FileExistsError(
            f"窗口目录已存在且非空: {window_root}；确认续跑时请加 --resume"
        )
    shutil.rmtree(window_root)
    window_root.mkdir(parents=True)


ROLLING_ROOT = PROJECT_ROOT / "outputs_new" / "zz500"
FULL_VALUE_ROOT = PROJECT_ROOT / "outputs" / "zz500" / "factor_value"
FINAL_ROOT = ROLLING_ROOT / "final"
START_DATE = pd.NaT
FIRST_LIVE_MONTH = pd.Period(DEFAULT_FIRST_MONTH, freq="M") + 1
FINAL_MONTH = pd.Period(DEFAULT_FINAL_MONTH, freq="M") + 1
FINAL_DATE = FINAL_MONTH.end_time.normalize()


def _winner_table(
    window: Path,
    category_names: list[str],
    factor_to_category: dict[str, str],
    selections_per_category: int = 1,
) -> pd.DataFrame:
    ic = pd.read_parquet(window / "ic.parquet")
    if (set(ic.columns) != {"factor_name", "IC_mean"}
            or ic["factor_name"].duplicated().any()
            or set(ic["factor_name"]) != set(factor_to_category)):
        raise ValueError(f"{window}/ic.parquet 结构或因子数量错误")
    ic["category_cn"] = ic["factor_name"].map(factor_to_category)
    if ic["category_cn"].isna().any():
        raise ValueError(f"{window}/ic.parquet 存在未分类因子")
    ic["IC_mean"] = pd.to_numeric(ic["IC_mean"], errors="coerce")
    ic = ic[np.isfinite(ic["IC_mean"])].copy()
    ic["abs_IC_mean"] = ic["IC_mean"].abs()
    if selections_per_category == 1:
        winners = (
            ic.sort_values(
                ["category_cn", "abs_IC_mean", "factor_name"],
                ascending=[True, False, True],
                kind="mergesort",
            )
            .groupby("category_cn", sort=False)
            .head(1)
        )
        winners["selection_rank"] = 1
    else:
        selection_path = window / "selected_factors.parquet"
        if not selection_path.is_file():
            raise FileNotFoundError(f"{window} 缺少 selected_factors.parquet")
        selected = pd.read_parquet(selection_path)
        required = {"category_cn", "selection_rank", "factor_name", "IC_mean"}
        if not required.issubset(selected.columns):
            raise ValueError(f"{selection_path} 缺少字段: {sorted(required)}")
        selected["selection_rank"] = pd.to_numeric(
            selected["selection_rank"], errors="raise"
        ).astype(int)
        if selected["factor_name"].duplicated().any():
            raise ValueError(f"{selection_path} 存在重复入选因子")
        expected_ranks = set(range(1, selections_per_category + 1))
        for category_name in category_names:
            ranks = set(
                selected.loc[
                    selected["category_cn"].eq(category_name), "selection_rank"
                ]
            )
            if ranks != expected_ranks:
                raise ValueError(
                    f"{selection_path} 的 {category_name} 排名错误: {sorted(ranks)}"
                )
        validation = selected.merge(
            ic[["factor_name", "category_cn", "IC_mean"]],
            on="factor_name",
            how="left",
            suffixes=("_selected", "_ic"),
            validate="one_to_one",
        )
        if validation["category_cn_ic"].isna().any() or not validation[
            "category_cn_selected"
        ].eq(validation["category_cn_ic"]).all():
            raise ValueError(f"{selection_path} 因子类别与 ic.parquet 不一致")
        if not np.allclose(
            pd.to_numeric(validation["IC_mean_selected"], errors="coerce"),
            pd.to_numeric(validation["IC_mean_ic"], errors="coerce"),
            rtol=0,
            atol=5e-10,
            equal_nan=False,
        ):
            raise ValueError(f"{selection_path} 的 IC_mean 与 ic.parquet 不一致")
        winners = selected[
            ["category_cn", "selection_rank", "factor_name", "IC_mean"]
        ].copy()
    if set(winners["category_cn"]) != set(category_names):
        raise ValueError(f"{window} 未能选出全部十类因子")
    expected_count = len(category_names) * selections_per_category
    if len(winners) != expected_count:
        raise ValueError(f"{window} 预期 {expected_count} 个胜出因子，实际 {len(winners)}")
    return winners[["category_cn", "selection_rank", "factor_name", "IC_mean"]]


def _load_category_rules(configs: dict | None = None) -> tuple[list[str], dict[str, str]]:
    names, mapping = load_categories(configs)
    if names != list(CATEGORY_NAMES):
        raise ValueError(f"类别顺序或名称不符合预期: {names}")
    return names, mapping


def _parse_window_endpoint(window: Path) -> pd.Timestamp:
    return pd.to_datetime(window.name.removeprefix("after_"), format="%Y_%m_%d")


def _build_schedule(
    *,
    configs: dict | None = None,
    require_window_reports: bool = True,
    selections_per_category: int = 1,
    selection_first_month: str = DEFAULT_FIRST_MONTH,
    selection_final_month: str = DEFAULT_FINAL_MONTH,
) -> pd.DataFrame:
    global START_DATE, FIRST_LIVE_MONTH, FINAL_DATE, FINAL_MONTH
    category_names, factor_to_category = _load_category_rules(configs)
    calendar = _load_full_calendar(_SELECTION_CONSTITUENTS)
    windows = sorted(
        ROLLING_ROOT.glob("after_*"),
        key=_parse_window_endpoint,
    )
    endpoints = [_parse_window_endpoint(window) for window in windows]
    endpoint_months = [date.to_period("M") for date in endpoints]
    first_selection = pd.Period(selection_first_month, freq="M")
    final_selection = pd.Period(selection_final_month, freq="M")
    if first_selection > final_selection:
        raise ValueError("selection_first_month 不能晚于 selection_final_month")
    expected_months = list(
        pd.period_range(first_selection, final_selection, freq="M")
    )
    target_months = [month + 1 for month in expected_months]
    FIRST_LIVE_MONTH = target_months[0]
    FINAL_MONTH = target_months[-1]
    first_target_dates = calendar[calendar.to_period("M") == FIRST_LIVE_MONTH]
    final_target_dates = calendar[calendar.to_period("M") == FINAL_MONTH]
    if first_target_dates.empty or final_target_dates.empty:
        raise ValueError(
            f"目标月份缺少交易日: {FIRST_LIVE_MONTH} 至 {FINAL_MONTH}"
        )
    START_DATE = pd.Timestamp(first_target_dates[0]).normalize()
    FINAL_DATE = pd.Timestamp(final_target_dates[-1]).normalize()
    if endpoint_months != expected_months:
        raise ValueError(
            "滚动窗口月份不连续或边界错误: "
            f"预期={expected_months[0] if expected_months else None}"
            f"至{expected_months[-1] if expected_months else None}, "
            f"实际={endpoint_months[0] if endpoint_months else None}"
            f"至{endpoint_months[-1] if endpoint_months else None}"
        )
    for window in windows:
        expected = len(category_names) * selections_per_category
        if require_window_reports and len(list(window.glob("factor_report/*/factor_report.md"))) != expected:
            raise ValueError(f"{window} 缺少 {expected} 份正式报告")
        if len(list(window.glob("*/raw.parquet"))) != expected:
            raise ValueError(f"{window} 缺少 {expected} 个胜出因子值目录")

    winner_by_window: dict[Path, pd.DataFrame] = {
        window: _winner_table(
            window,
            category_names,
            factor_to_category,
            selections_per_category,
        )
        for window in windows
    }
    records: list[dict[str, Any]] = []

    # 每个目标月使用上一个月末已经确定的胜出因子身份；下一月数值从
    # 只读全时段因子库提取，因为 after_* 目录只保存到其自身月末。
    for position, target_month in enumerate(target_months):
        selection_window = windows[position]
        winners = winner_by_window[selection_window].set_index(
            ["category_cn", "selection_rank"]
        )
        for category_cn in category_names:
            for selection_rank in range(1, selections_per_category + 1):
                winner = winners.loc[(category_cn, selection_rank)]
                category_en = CATEGORY_NAMES[category_cn]
                final_factor_name = (
                    category_en
                    if selections_per_category == 1
                    else f"{category_en}_{selection_rank}"
                )
                records.append({
                    "target_period": str(target_month),
                    "target_start": target_month.start_time.normalize(),
                    "target_end": target_month.end_time.normalize(),
                    "selection_window": selection_window.name,
                    "category_cn": category_cn,
                    "category_en": final_factor_name,
                    "selection_rank": selection_rank,
                    "source_factor": winner["factor_name"],
                    "selected_IC_mean": float(winner["IC_mean"]),
                    "direction_multiplier": (
                        1.0 if float(winner["IC_mean"]) >= 0 else -1.0
                    ),
                    "value_root": portable_path(FULL_VALUE_ROOT),
                    "value_source": "full_value_library_read_only",
                })
    schedule = pd.DataFrame.from_records(records)
    expected_rows = len(target_months) * len(category_names) * selections_per_category
    if len(schedule) != expected_rows:
        raise ValueError(f"拼接计划预期 {expected_rows} 行，实际 {len(schedule)}")
    return schedule


def _merge_category(task: tuple[str, str, list[dict[str, Any]], str]) -> dict[str, Any]:
    category_cn, category_en, segment_records, final_root_text = task
    final_root = Path(final_root_text)
    temporary = final_root / f".{category_en}.{uuid.uuid4().hex}.tmp"
    destination = final_root / category_en
    try:
        temporary_factors = temporary / "factors"
        temporary_factors.mkdir(parents=True)
        source_dirs = {
            resolve_project_path(record["value_root"]) / record["source_factor"]
            for record in segment_records
        }
        missing_dirs = [str(path) for path in source_dirs if not path.is_dir()]
        if missing_dirs:
            raise FileNotFoundError(f"来源因子目录不存在: {missing_dirs[:5]}")
        symbols = sorted(
            {
                symbol
                for source_dir in source_dirs
                for symbol in _factor_symbols(source_dir)
            }
        )
        if not symbols:
            raise ValueError(f"{category_cn} 没有任何股票因子文件")

        raw_out = f"{category_en}_raw"
        neutral_out = f"{category_en}_neutralization"
        total_rows = 0
        cells_filled = 0
        written_files = 0
        for symbol in symbols:
            cache: dict[tuple[str, str], pd.DataFrame | None] = {}
            pieces: list[pd.DataFrame] = []
            for record in segment_records:
                source_factor = str(record["source_factor"])
                direction_multiplier = float(record["direction_multiplier"])
                if direction_multiplier not in {-1.0, 1.0}:
                    raise ValueError(
                        f"{category_en}/{record['target_period']} 的方向乘数非法: "
                        f"{direction_multiplier}"
                    )
                value_root = str(record["value_root"])
                cache_key = (value_root, source_factor)
                if cache_key not in cache:
                    frame = _read_factor_stock(resolve_project_path(value_root) / source_factor, source_factor, symbol)
                    cache[cache_key] = frame
                source = cache[cache_key]
                if source is None:
                    continue
                start = pd.Timestamp(record["target_start"])
                end = pd.Timestamp(record["target_end"])
                piece = source.loc[source["signal_date"].between(start, end)].copy()
                if piece.empty:
                    continue
                raw_source = f"{source_factor}_raw"
                neutral_source = f"{source_factor}_neutralization"
                piece = piece.rename(
                    columns={raw_source: raw_out, neutral_source: neutral_out}
                )
                for column in (raw_out, neutral_out):
                    values = pd.to_numeric(piece[column], errors="coerce").replace(
                        [np.inf, -np.inf], np.nan
                    )
                    cells_filled += int(values.isna().sum())
                    # 月内仅使用当日以前的值；月初仍为空时补 0，禁止用
                    # 月内未来值反向填充。
                    piece[column] = (
                        _fill_selected_series(piece, symbol, values) * direction_multiplier
                    )
                pieces.append(
                    piece[["signal_date", "available_date", raw_out, neutral_out]]
                )
            if not pieces:
                continue
            merged = pd.concat(pieces, ignore_index=True).sort_values(
                "signal_date", kind="mergesort"
            )
            if merged["signal_date"].duplicated().any():
                raise ValueError(f"{category_en}/{symbol} 出现重复 signal_date")
            merged = merged.loc[_member_rows(merged, symbol)].copy()
            if merged.empty:
                continue
            portable_frame(merged).to_parquet(
                temporary_factors / f"{symbol}.parquet",
                index=False,
            )
            total_rows += len(merged)
            written_files += 1
        if not written_files or not total_rows:
            raise ValueError(f"{category_cn} 未生成任何合并数据")

        # 前段已按股票前向填充并补0，这里只检查，不再用全区间统计量补值。
        min_date: pd.Timestamp | None = None
        max_date: pd.Timestamp | None = None
        for path in sorted(temporary_factors.glob("*.parquet")):
            frame = pd.read_parquet(path)
            if not np.isfinite(frame[[raw_out, neutral_out]].to_numpy(dtype=float)).all():
                raise ValueError(f"{category_en} 填充后仍有无效因子值: {path.name}")
            current_min = frame["signal_date"].min()
            current_max = frame["signal_date"].max()
            min_date = current_min if min_date is None else min(min_date, current_min)
            max_date = current_max if max_date is None else max(max_date, current_max)
        if min_date != START_DATE or max_date != FINAL_DATE:
            raise ValueError(
                f"{category_en} 日期范围错误: {min_date} 至 {max_date}"
            )
        _consolidate_factor_staging(temporary, category_en)
        if destination.exists():
            shutil.rmtree(destination)
        temporary.replace(destination)
        return {
            "category_cn": category_cn,
            "category_en": category_en,
            "status": "completed",
            "files": written_files,
            "rows": total_rows,
            "cells_filled": cells_filled,
        }
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
        return {
            "category_cn": category_cn,
            "category_en": category_en,
            "status": "failed",
            "traceback": traceback.format_exc(),
        }


def _write_manifest(schedule: pd.DataFrame, final_root: Path) -> None:
    write_output_parquet(
        schedule.drop(columns=["value_root"]), final_root / "selection_schedule.parquet"
    )


def _load_report_market_data() -> tuple[pd.DataFrame, FactorDataLoader]:
    if _SELECTION_CONSTITUENT_INDEX != "000905.SH":
        raise ValueError("当前分区行情仅配置中证500，其他股票池需提供独立数据来源")
    loader = FactorDataLoader(
        runtime_inputs=legacy.runtime_inputs(
            "zz500", stock_day=_SELECTION_DATA_DIR, constituents=_SELECTION_CONSTITUENTS
        ),
        universe="zz500", context_only=True,
        start=START_DATE.strftime("%Y-%m-%d"), end=FINAL_DATE.strftime("%Y-%m-%d"),
    )
    return loader.load_all(apply_universe_filters=False).sort_index(), loader


def _build_reports(
    final_root: Path,
    workers: int,
    selection_rule: str,
    selections_per_category: int = 1,
) -> None:
    """合并后的日频因子统一接入IC、精细收益及MD/HTML报告阶段。"""
    market_data, loader = _load_report_market_data()
    configs = {}
    for category_cn, category_en in CATEGORY_NAMES.items():
        for rank in range(1, selections_per_category + 1):
            name = category_en if selections_per_category == 1 else f"{category_en}_{rank}"
            configs[name] = {
                "category": category_cn,
                "description": (
                    f"{category_cn}类别第{rank}个滚动筛选因子；上一月末确定来源因子，"
                    "按该次筛选的历史IC符号对齐后使用其日频值。"
                    "本报告方向另按合并后因子自身的全时段IC确定。"
                ),
                "formula": (
                    r"$F_i(t)=\operatorname{sign}(\overline{IC}_{f^*,m-1})"
                    r"\,f^*_i(t)$；t属于目标月m，f*由上一月末筛选；"
                    "逐月来源和方向见final/selection_schedule.parquet。"
                ),
                "params": {"selection_rule": selection_rule, "category_cn": category_cn},
            }
    legacy._PIPELINE_CONFIGS = configs
    legacy._PIPELINE_FINANCIAL_FACTORS = set()
    legacy._PIPELINE_UNIVERSE_NAME = "中证500"
    legacy._PIPELINE_OUTPUT_ROOT = final_root.resolve()
    legacy._PIPELINE_IC_OUTPUT_ROOT = final_root.parent / "factor_ic"
    legacy._PIPELINE_RETURN_OUTPUT_ROOT = final_root.parent / "factor_return"
    legacy._PIPELINE_MARKET_DATA = market_data
    legacy._PIPELINE_CALENDAR = loader.trading_calendar
    legacy._PIPELINE_CONSTITUENTS = loader.constituents
    legacy._PIPELINE_DATES = pd.DatetimeIndex(
        market_data.index.get_level_values("date").unique()
    ).sort_values()
    legacy._PIPELINE_SYMBOLS = sorted(market_data.index.get_level_values("symbol").unique())

    # 缺失检查仅覆盖当日成分股，不能把非成分单元当作需要补齐的样本。
    for name in configs:
        for version, values in legacy._load_saved_versions(name).items():
            mask = daily_member_mask(values, loader.constituents)
            if (mask & ~np.isfinite(values)).any().any():
                raise ValueError(f"{name}/{version} 当日成分股存在无效因子值")

    legacy._run_report_stages(
        list(configs), min(max(1, workers), len(configs)),
        execution_prices=_SELECTION_DATA_DIR,
        constituents_path=_SELECTION_CONSTITUENTS,
    )


DEFAULT_MERGE_WORKERS = len(CATEGORY_NAMES)
WINDOW_TRADING_DAYS = {
    "6m": 126,
    "1y": 252,
    "2y": 504,
    "3y": 756,
}
DEFAULT_SELECTIONS_PER_CATEGORY = {
    "6m": 1,
    "1y": 3,
    "2y": 3,
    "3y": 1,
}
DEFAULT_MAX_ABS_CORRELATION = 0.70
FORWARD_PRICE_DAYS = 6
IC_PERIOD = 5

_WINDOW_IC_STARTS: tuple[pd.Timestamp, ...] = ()
_WINDOW_FACTOR_ENDS: tuple[pd.Timestamp, ...] = ()
_FACTOR_VALUE_CACHE: dict[str, pd.Series] = {}
_PAIR_DAILY_CORRELATION_CACHE: dict[tuple[str, str], pd.Series] = {}


def _result(name: str, status: str, **extra: Any) -> dict[str, Any]:
    return {"factor": name, "status": status, **extra}


def _build_recent_windows(
    calendar: pd.DatetimeIndex,
    first_month: str,
    final_month: str,
    recent_days: int,
) -> list[tuple[pd.Period, pd.Timestamp, pd.Timestamp, pd.Timestamp]]:
    if recent_days <= FORWARD_PRICE_DAYS:
        raise ValueError(
            f"recent_days 必须大于尾部收益价格日数 {FORWARD_PRICE_DAYS}"
        )
    first = pd.Period(first_month, freq="M")
    final = pd.Period(final_month, freq="M")
    if first > final:
        raise ValueError("first-month 不能晚于 final-month")
    windows = []
    for month in pd.period_range(first, final, freq="M"):
        month_dates = calendar[
            (calendar >= month.start_time.normalize())
            & (calendar <= month.end_time.normalize())
        ]
        if month_dates.empty:
            raise ValueError(f"{month} 没有交易日")
        endpoint = month_dates[-1]
        position = calendar.get_loc(endpoint)
        if not isinstance(position, (int, np.integer)):
            raise ValueError(f"{endpoint:%Y-%m-%d} 在交易日历中不唯一")
        if position < recent_days - 1:
            raise ValueError(f"{month} 之前不足 {recent_days} 个交易日")
        window_start = calendar[position - recent_days + 1]
        factor_end = calendar[position - FORWARD_PRICE_DAYS]
        if len(calendar[(calendar >= window_start) & (calendar <= endpoint)]) != recent_days:
            raise ValueError(f"{month} 的最近交易日窗口不是 {recent_days} 日")
        windows.append((month, endpoint, window_start, factor_end))
    return windows


def _aggregate_recent_ic_means(
    ic_series: pd.Series,
    starts: tuple[pd.Timestamp, ...],
    ends: tuple[pd.Timestamp, ...],
    period: int = IC_PERIOD,
) -> list[float]:
    series = ic_series.sort_index()
    dates = pd.DatetimeIndex(series.index).to_numpy(dtype="datetime64[ns]")
    values = series.to_numpy(dtype="float64")
    results = []
    for start, end in zip(starts, ends, strict=True):
        left = int(np.searchsorted(dates, np.datetime64(start.to_datetime64()), side="left"))
        right = int(np.searchsorted(dates, np.datetime64(end.to_datetime64()), side="right"))
        recent_values = values[left:right]
        means = []
        for offset in range(period):
            offset_values = recent_values[offset::period]
            valid = offset_values[np.isfinite(offset_values)]
            if valid.size:
                means.append(float(valid.mean()))
        results.append(float(np.mean(means)) if means else np.nan)
    return results


def _calculate_factor_recent_ic(name: str) -> dict[str, Any]:
    try:
        ic_series = _load_saved_ic_series(name)
        ic_means = _aggregate_recent_ic_means(
            ic_series, _WINDOW_IC_STARTS, _WINDOW_FACTOR_ENDS
        )
        return _result(name, "completed", IC_means=ic_means)
    except Exception:
        return _result(name, "failed", traceback=traceback.format_exc())


def _load_cached_factor(name: str) -> pd.Series:
    factor = _FACTOR_VALUE_CACHE.get(name)
    if factor is None:
        factor = _load_source_factor_series(name)
        _FACTOR_VALUE_CACHE[name] = factor
    return factor


def _mean_window_abs_spearman(
    left_name: str,
    right_name: str,
    window_start: pd.Timestamp,
    factor_end: pd.Timestamp,
) -> float:
    """逐日横截面 Spearman 保留符号，先取窗口均值，再取绝对值。"""
    pair = tuple(sorted((left_name, right_name)))
    daily = _PAIR_DAILY_CORRELATION_CACHE.get(pair)
    if daily is None:
        left = _load_cached_factor(pair[0]).rename("left")
        right = _load_cached_factor(pair[1]).rename("right")
        combined = pd.concat([left, right], axis=1, join="inner").replace(
            [np.inf, -np.inf], np.nan
        ).dropna()
        if combined.empty:
            daily = pd.Series(dtype="float64")
        else:
            ranks = combined.groupby(level="date", sort=True).rank(method="average")
            ranks["xy"] = ranks["left"] * ranks["right"]
            ranks["xx"] = ranks["left"] ** 2
            ranks["yy"] = ranks["right"] ** 2
            grouped = ranks.groupby(level="date", sort=True)
            count = grouped["left"].count().astype("float64")
            sum_x = grouped["left"].sum()
            sum_y = grouped["right"].sum()
            numerator = count * grouped["xy"].sum() - sum_x * sum_y
            denominator = np.sqrt(
                (count * grouped["xx"].sum() - sum_x**2)
                * (count * grouped["yy"].sum() - sum_y**2)
            )
            daily = numerator / denominator
            daily[(count < 3) | (denominator <= 0)] = np.nan
            daily.index = pd.DatetimeIndex(daily.index)
        _PAIR_DAILY_CORRELATION_CACHE[pair] = daily.sort_index()
    window = daily.loc[(daily.index >= window_start) & (daily.index <= factor_end)]
    return float(abs(window.mean())) if window.notna().any() else np.nan


def _select_diversified_winners(
    ic_frame: pd.DataFrame,
    category_names: list[str],
    factor_to_category: dict[str, str],
    window_start: pd.Timestamp,
    factor_end: pd.Timestamp,
    selections_per_category: int,
    max_abs_correlation: float,
    *,
    rank_by_signed_ic: bool = False,
    backfill_without_correlation: bool = False,
    allow_equal_correlation: bool = False,
) -> pd.DataFrame:
    values = ic_frame.copy()
    values["category_cn"] = values["factor_name"].map(factor_to_category)
    values["IC_mean"] = pd.to_numeric(values["IC_mean"], errors="coerce")
    values = values[np.isfinite(values["IC_mean"])].copy()
    values["abs_IC_mean"] = values["IC_mean"].abs()
    ranking_column = "IC_mean" if rank_by_signed_ic else "abs_IC_mean"
    records: list[dict[str, Any]] = []
    for category_name in category_names:
        candidates = values.loc[values["category_cn"].eq(category_name)].sort_values(
            [ranking_column, "factor_name"],
            ascending=[False, True],
            kind="mergesort",
        )
        chosen: list[str] = []
        for candidate in candidates.itertuples(index=False):
            correlations = [
                _mean_window_abs_spearman(
                    str(candidate.factor_name), other, window_start, factor_end
                )
                for other in chosen
            ]
            correlation_rejected = any(
                not np.isfinite(value)
                or (
                    value > max_abs_correlation
                    if allow_equal_correlation
                    else value >= max_abs_correlation
                )
                for value in correlations
            )
            if correlation_rejected:
                continue
            chosen.append(str(candidate.factor_name))
            records.append({
                "category_cn": category_name,
                "selection_rank": len(chosen),
                "factor_name": str(candidate.factor_name),
                "IC_mean": float(candidate.IC_mean),
                "abs_IC_mean": float(candidate.abs_IC_mean),
                "selection_stage": "correlation_limited",
                "max_abs_correlation_to_earlier_selected": (
                    max(correlations) if correlations else 0.0
                ),
            })
            if len(chosen) == selections_per_category:
                break

        # 第二阶段：若相关性约束阶段不足目标数量，则按有符号 IC 从大到小，
        # 从未入选因子中补足。所有类别（包括成长类）使用同一规则。
        if backfill_without_correlation and len(chosen) < selections_per_category:
            chosen_set = set(chosen)
            for candidate in candidates.itertuples(index=False):
                factor_name = str(candidate.factor_name)
                if factor_name in chosen_set:
                    continue
                correlations = [
                    _mean_window_abs_spearman(
                        factor_name, other, window_start, factor_end
                    )
                    for other in chosen
                ]
                chosen.append(factor_name)
                chosen_set.add(factor_name)
                finite_correlations = [
                    value for value in correlations if np.isfinite(value)
                ]
                records.append({
                    "category_cn": category_name,
                    "selection_rank": len(chosen),
                    "factor_name": factor_name,
                    "IC_mean": float(candidate.IC_mean),
                    "abs_IC_mean": float(candidate.abs_IC_mean),
                    "selection_stage": "ic_backfill",
                    "max_abs_correlation_to_earlier_selected": (
                        max(finite_correlations) if finite_correlations else np.nan
                    ),
                })
                if len(chosen) == selections_per_category:
                    break
        if len(chosen) != selections_per_category:
            if backfill_without_correlation:
                raise ValueError(
                    f"类别{category_name}只有{len(candidates)}个有限 IC 因子，"
                    f"无法补足{selections_per_category}个"
                )
            raise ValueError(
                f"类别{category_name}只能选出{len(chosen)}个低相关因子"
            )
    return pd.DataFrame.from_records(records)


def _completed_window_ready(
    window_root: Path,
    factor_names: set[str],
    category_names: list[str],
    factor_to_category: dict[str, str],
    selections_per_category: int,
) -> bool:
    ic_path = window_root / "ic.parquet"
    if not ic_path.is_file():
        return False
    try:
        ic = pd.read_parquet(ic_path)
        if (
            list(ic.columns) != ["factor_name", "IC_mean"]
            or len(ic) != len(factor_names)
            or set(ic["factor_name"]) != factor_names
        ):
            return False
        if selections_per_category == 1:
            selected = _select_category_winners(
                ic, category_names, factor_to_category
            )
            expected = {name for name, _ in selected.values()}
        else:
            selected = pd.read_parquet(window_root / "selected_factors.parquet")
            expected = set(selected["factor_name"])
            if len(expected) != len(category_names) * selections_per_category:
                return False
        factor_dirs = {
            path.parent.name for path in window_root.glob("*/raw.parquet") if path.is_file()
        }
        return factor_dirs == expected
    except Exception:
        return False


def _run_merge_tasks(
    schedule: pd.DataFrame,
    final_root: Path,
    merge_workers: int,
) -> None:
    tasks = []
    for category_en, subset in schedule.groupby("category_en", sort=True):
        category_cn = str(subset.iloc[0]["category_cn"])
        tasks.append(
            (category_cn, str(category_en), subset.to_dict(orient="records"), str(final_root))
        )
    failures = []
    context = mp.get_context("fork")
    with ProcessPoolExecutor(
        max_workers=min(max(1, merge_workers), len(tasks)), mp_context=context
    ) as executor:
        futures = {executor.submit(_merge_category, task): task for task in tasks}
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="十类近期滚动因子拼接", unit="category"
        ):
            result = future.result()
            if result["status"] == "failed":
                failures.append(result)
                tqdm.write(f"FAILED {result['category_en']}\n{result['traceback']}")
            else:
                tqdm.write(
                    f"MERGE_DONE category={result['category_en']} files={result['files']} "
                    f"rows={result['rows']} cells_filled={result['cells_filled']}"
                )
    if failures:
        raise RuntimeError(f"近期滚动因子拼接失败: {len(failures)}")


def _build_final(
    *,
    configs: dict | None = None,
    output_root: Path,
    source_root: Path,
    workers: int,
    merge_workers: int,
    recent_days: int,
    selections_per_category: int,
    max_abs_correlation: float | None,
    selection_first_month: str = DEFAULT_FIRST_MONTH,
    selection_final_month: str = DEFAULT_FINAL_MONTH,
) -> None:
    global FINAL_ROOT, FULL_VALUE_ROOT, ROLLING_ROOT
    final_root = output_root / "final"
    if final_root.exists():
        shutil.rmtree(final_root)
    final_root.mkdir(parents=True)
    ROLLING_ROOT = output_root
    FULL_VALUE_ROOT = source_root
    FINAL_ROOT = final_root
    schedule = _build_schedule(
        configs=configs,
        require_window_reports=False,
        selections_per_category=selections_per_category,
        selection_first_month=selection_first_month,
        selection_final_month=selection_final_month,
    )
    _write_manifest(schedule, final_root)
    _run_merge_tasks(schedule, final_root, merge_workers)
    if selections_per_category == 1:
        selection_rule = (
            f"previous_month_recent_{recent_days}_trading_days_max_abs_IC_mean"
        )
    else:
        selection_rule = (
            f"previous_month_recent_{recent_days}_trading_days_max_abs_IC_mean_"
            f"top{selections_per_category}_pairwise_abs_spearman_below_"
            f"{max_abs_correlation}"
        )
    _build_reports(
        final_root,
        workers,
        selection_rule=selection_rule,
        selections_per_category=selections_per_category,
    )
    print(
        f"FINAL_DONE output={final_root} "
        f"reports={len(CATEGORY_NAMES) * selections_per_category}",
        flush=True,
    )


def _write_monthly_selection_report(
    *,
    report_path: Path,
    source_root: Path,
    output_root: Path,
    windows: list[tuple[pd.Period, pd.Timestamp, pd.Timestamp, pd.Timestamp]],
    category_names: list[str],
    factor_to_category: dict[str, str],
    selections_per_category: int,
    ic_version: str,
    recent_days: int,
) -> Path:
    """记录每个筛选月选中的因子，以及其下一应用月份。"""
    category_order = {name: position for position, name in enumerate(category_names)}
    lines = [
        "# 三年滚动 IC 月度入选因子记录",
        "",
        f"- 因子值来源：`{source_root}`",
        f"- 结果目录：`{output_root}`",
        f"- IC 因子版本：`{ic_version}`",
        f"- 回看窗口：最近 {recent_days} 个交易日",
        "- IC 口径：Spearman Rank IC，T+1 收盘买入、T+6 收盘卖出",
        f"- 每类入选数量：{selections_per_category}",
        "- 排序规则：按 `|IC_mean|` 降序，绝对值相同时按因子名升序",
        "",
        "> “应用月份”使用上一筛选月末已经确定的因子。末月筛选结果可能对应当前结果区间之外的下一个月。",
        "",
    ]
    total_selected = 0
    for month, endpoint, window_start, factor_end in windows:
        window_root = output_root / f"after_{endpoint:%Y_%m_%d}"
        winners = _winner_table(
            window_root,
            category_names,
            factor_to_category,
            selections_per_category,
        ).copy()
        winners["_category_order"] = winners["category_cn"].map(category_order)
        winners = winners.sort_values(
            ["_category_order", "selection_rank", "factor_name"],
            kind="mergesort",
        )
        effective_month = month + 1
        lines.extend([
            f"## {month} 筛选（应用于 {effective_month}）",
            "",
            (
                f"IC 数据范围：{window_start:%Y-%m-%d} 至 "
                f"{factor_end:%Y-%m-%d}；筛选月末：{endpoint:%Y-%m-%d}。"
            ),
            "",
            r"| 类别 | 排名 | 因子名 | IC_mean | \|IC_mean\| |",
            "|---|---:|---|---:|---:|",
        ])
        for row in winners.itertuples(index=False):
            ic_mean = float(row.IC_mean)
            lines.append(
                f"| {row.category_cn} | {int(row.selection_rank)} | "
                f"`{row.factor_name}` | {ic_mean:.10f} | {abs(ic_mean):.10f} |"
            )
            total_selected += 1
        lines.append("")
    expected = len(windows) * len(category_names) * selections_per_category
    if total_selected != expected:
        raise ValueError(
            f"月度入选报告记录数错误: expected={expected}, actual={total_selected}"
        )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = report_path.with_suffix(report_path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(portable_payload("\n".join(lines).rstrip() + "\n"), encoding="utf-8")
    temporary.replace(report_path)
    return report_path


def run_pipeline(
    *,
    window: str,
    expansion_config_path: Path,
    base_config_path: Path,
    source_root: Path,
    ic_root: Path,
    output_root: Path | None,
    selection_report_path: Path | None,
    start: str,
    first_month: str,
    final_month: str,
    workers: int,
    merge_workers: int,
    resume: bool,
    ic_version: str,
    plan_only: bool,
    data_dir: Path,
    constituents: Path,
    constituent_index: str,
    selections_per_category: int | None = None,
    max_abs_correlation: float | None = None,
) -> None:
    global _IC_ROOT, _IC_VERSION, _SOURCE_ROOT
    global _WINDOW_IC_STARTS, _WINDOW_FACTOR_ENDS
    global _SELECTION_DATA_DIR, _SELECTION_CONSTITUENTS
    global _SELECTION_CONSTITUENT_INDEX
    if window not in WINDOW_TRADING_DAYS:
        raise ValueError(f"window只能是{', '.join(WINDOW_TRADING_DAYS)}")
    recent_days = WINDOW_TRADING_DAYS[window]
    if selections_per_category is None:
        selections_per_category = DEFAULT_SELECTIONS_PER_CATEGORY[window]
    if selections_per_category < 1:
        raise ValueError("selections_per_category必须大于等于1")
    if selections_per_category > 1 and max_abs_correlation is None:
        max_abs_correlation = DEFAULT_MAX_ABS_CORRELATION
    if max_abs_correlation is not None and not 0 <= max_abs_correlation < 1:
        raise ValueError("max_abs_correlation必须在[0, 1)内")
    workers = max(1, workers)
    _SELECTION_DATA_DIR = data_dir.resolve()
    _SELECTION_CONSTITUENTS = constituents.resolve()
    _SELECTION_CONSTITUENT_INDEX = constituent_index
    source_root = source_root.resolve()
    ic_root = ic_root.resolve()
    if output_root is None:
        output_root = PROJECT_ROOT / f"factors_value_ic_{window}"
    output_root = output_root.resolve()
    if selection_report_path is None:
        selection_report_path = (
            PROJECT_ROOT / f"factors_value_ic_{window}_monthly_selected_factors.md"
        )
    selection_report_path = selection_report_path.resolve()
    _assert_source_is_read_only_scope(source_root, output_root)
    _SOURCE_ROOT = source_root
    _IC_ROOT = ic_root
    _IC_VERSION = ic_version
    configs = _load_configs(expansion_config_path, base_config_path)
    factor_names = sorted(configs)
    category_names, factor_to_category = _load_categories(
        configs, set(factor_names)
    )
    _validate_source_factor_dirs(source_root, factor_names)
    _validate_ic_files(ic_root, factor_names)
    calendar = _read_trading_calendar(start, final_month)
    legacy._PIPELINE_DATES = calendar
    windows = _build_recent_windows(calendar, first_month, final_month, recent_days)
    _WINDOW_IC_STARTS = tuple(item[2] for item in windows)
    _WINDOW_FACTOR_ENDS = tuple(item[3] for item in windows)
    print(
        f"RECENT_PLAN window={window} factors={len(factor_names)} windows={len(windows)} "
        f"recent_days={recent_days} selections_per_category={selections_per_category} "
        f"IC_source={ic_root}",
        flush=True,
    )
    if plan_only:
        return
    output_root.mkdir(parents=True, exist_ok=True)
    results = _run_parallel_collect(
        _calculate_factor_recent_ic,
        factor_names,
        workers,
        "全因子近期每日IC及多窗口聚合",
    )
    result_by_name = {result["factor"]: result for result in results}
    for position, (month, endpoint, window_start, factor_end) in enumerate(windows):
        window_root = output_root / f"after_{endpoint:%Y_%m_%d}"
        if resume and _completed_window_ready(
            window_root,
            set(factor_names),
            category_names,
            factor_to_category,
            selections_per_category,
        ):
            continue
        _prepare_window_directory(window_root, resume)
        ic = pd.DataFrame({
            "factor_name": factor_names,
            "IC_mean": [result_by_name[name]["IC_means"][position] for name in factor_names],
        })
        write_output_parquet(ic, window_root / "ic.parquet")
        if selections_per_category == 1:
            winner_map = _select_category_winners(
                ic, category_names, factor_to_category
            )
            selected = pd.DataFrame([
                {
                    "category_cn": category,
                    "selection_rank": 1,
                    "factor_name": name,
                    "IC_mean": value,
                }
                for category, (name, value) in winner_map.items()
            ])
        else:
            selected = _select_diversified_winners(
                ic,
                category_names,
                factor_to_category,
                window_start,
                factor_end,
                selections_per_category,
                float(max_abs_correlation),
            )
            write_output_parquet(
                selected, window_root / "selected_factors.parquet"
            )
        winner_names = sorted(set(selected["factor_name"]))
        tasks = [
            (name, start, endpoint.strftime("%Y-%m-%d"), str(window_root))
            for name in winner_names
        ]
        _run_parallel_collect(
            _materialize_filled_factor,
            tasks,
            min(workers, len(tasks)),
            f"{month} 胜出因子复制与补齐",
        )
        print(
            f"WINDOW_DONE endpoint={endpoint:%Y-%m-%d} "
            f"window_start={window_start:%Y-%m-%d} factor_end={factor_end:%Y-%m-%d} "
            f"ic_factors={len(ic)} filled_factors={len(winner_names)} reports=0 "
            f"output={window_root}",
            flush=True,
        )
    _build_final(
        configs=configs,
        output_root=output_root,
        source_root=source_root,
        workers=workers,
        merge_workers=merge_workers,
        recent_days=recent_days,
        selections_per_category=selections_per_category,
        max_abs_correlation=max_abs_correlation,
        selection_first_month=first_month,
        selection_final_month=final_month,
    )
    report_path = _write_monthly_selection_report(
        report_path=selection_report_path,
        source_root=source_root,
        output_root=output_root,
        windows=windows,
        category_names=category_names,
        factor_to_category=factor_to_category,
        selections_per_category=selections_per_category,
        ic_version=ic_version,
        recent_days=recent_days,
    )
    print(f"SELECTION_REPORT_DONE output={report_path}", flush=True)

DEFAULT_RETURN_ROOT = PROJECT_ROOT / "outputs" / "zz500" / "factor_return"
RETURN_DEFAULT_SOURCE_ROOT = PROJECT_ROOT / "outputs" / "zz500" / "factor_value"
RETURN_DEFAULT_FIRST_MONTH = "2019-12"
RETURN_DEFAULT_FINAL_MONTH = "2026-05"
RETURN_DEFAULT_WORKERS = 20
RETURN_DEFAULT_MERGE_WORKERS = len(CATEGORY_NAMES)
RETURN_DEFAULT_SELECTIONS_PER_CATEGORY = 3
RETURN_DEFAULT_MAX_ABS_CORRELATION = 0.70
WINDOW_LOOKBACK_MONTHS = {
    "6m": 6,
    "1y": 12,
    "2y": 24,
    "3y": 36,
}
CATEGORY_ENGLISH = CATEGORY_NAMES


@dataclass(frozen=True)
class WindowSpec:
    month: pd.Period
    endpoint: pd.Timestamp
    raw_start: pd.Timestamp
    first_week_start: pd.Timestamp
    last_week_end: pd.Timestamp
    week_ids: tuple[str, ...]

    @property
    def target_month(self) -> pd.Period:
        return self.month + 1

    @property
    def directory_name(self) -> str:
        return f"after_{self.endpoint:%Y_%m_%d}"


_SCORE_RETURN_ROOT = DEFAULT_RETURN_ROOT
_SCORE_WINDOWS: tuple[WindowSpec, ...] = ()
_EXPECTED_AVAILABLE_DATES_BY_SYMBOL: dict[str, tuple[pd.Timestamp, ...]] = {}
_AVAILABLE_TO_SIGNAL_DATE: dict[pd.Timestamp, pd.Timestamp] = {}


def _initialize_final_constituent_grid(
    constituents: Path,
    schedule: pd.DataFrame,
) -> None:
    """准备最终因子必须覆盖的每日成分股与上一交易日映射。"""
    global _EXPECTED_AVAILABLE_DATES_BY_SYMBOL, _AVAILABLE_TO_SIGNAL_DATE
    frame = read_constituent_table(constituents)
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    calendar = pd.DatetimeIndex(frame["date"].drop_duplicates()).sort_values()
    previous = pd.Series(calendar[:-1].to_numpy(), index=calendar[1:])
    start = pd.to_datetime(schedule["target_start"], errors="raise").min()
    end = pd.to_datetime(schedule["target_end"], errors="raise").max()
    # 输出成员资格按 signal_date 判断，available_date 仅决定可交易月份。
    frame = frame.sort_values("date").copy()
    frame["tickers"] = frame["tickers"].shift(1)
    live = frame.loc[frame["date"].between(start, end)].copy()
    live["symbol"] = live["tickers"].str.split(",")
    live = live[["date", "symbol"]].explode("symbol", ignore_index=True)
    if live["symbol"].isna().any() or live["symbol"].eq("").any():
        raise ValueError("每日成分股文件存在空股票代码")
    if live.duplicated(["date", "symbol"]).any():
        raise ValueError("每日成分股文件存在重复(date, symbol)")
    missing_previous = live.loc[~live["date"].isin(previous.index), "date"].unique()
    if len(missing_previous):
        raise ValueError(f"以下交易日缺少上一交易日映射: {missing_previous[:5]}")
    _EXPECTED_AVAILABLE_DATES_BY_SYMBOL = {
        str(symbol): tuple(pd.DatetimeIndex(subset["date"]).sort_values())
        for symbol, subset in live.groupby("symbol", sort=False)
    }
    _AVAILABLE_TO_SIGNAL_DATE = {
        pd.Timestamp(date): pd.Timestamp(signal_date)
        for date, signal_date in previous.items()
        if start <= pd.Timestamp(date) <= end
    }


def _load_full_calendar(path: Path) -> pd.DatetimeIndex:
    frame = read_constituent_table(path)[["date"]]
    calendar = pd.DatetimeIndex(frame["date"].drop_duplicates()).sort_values()
    if calendar.empty:
        raise ValueError(f"交易日历为空: {path}")
    return calendar


def _week_id(last_trade: pd.Timestamp) -> str:
    iso = last_trade.isocalendar()
    return f"{int(iso.year):04d}-W{int(iso.week):02d}"


def _build_windows(
    calendar: pd.DatetimeIndex,
    first_month: str,
    final_month: str,
    lookback_months: int,
) -> list[WindowSpec]:
    first = pd.Period(first_month, freq="M")
    final = pd.Period(final_month, freq="M")
    if first > final:
        raise ValueError("first-month 不能晚于 final-month")

    grouped: dict[pd.Period, list[pd.Timestamp]] = {}
    for value in calendar:
        day = pd.Timestamp(value).normalize()
        grouped.setdefault(day.to_period("W-SUN"), []).append(day)
    complete_weeks = [
        (period, dates[0], dates[-1], _week_id(dates[-1]))
        for period, dates in sorted(grouped.items())
    ]
    absolute_last = pd.Timestamp(calendar[-1]).normalize()
    final_calendar_week = absolute_last.to_period("W-SUN")

    windows: list[WindowSpec] = []
    for month in pd.period_range(first, final, freq="M"):
        month_days = calendar[
            (calendar >= month.start_time.normalize())
            & (calendar <= month.end_time.normalize())
        ]
        if month_days.empty:
            raise ValueError(f"{month} 没有交易日")
        endpoint = pd.Timestamp(month_days[-1]).normalize()
        raw_start = endpoint - pd.DateOffset(months=lookback_months)
        selected: list[tuple[pd.Timestamp, pd.Timestamp, str]] = []
        for period, first_trade, last_trade, identifier in complete_weeks:
            if first_trade < raw_start or last_trade > endpoint:
                continue
            # 数据集最后一周停在周一至周四时，无法确认这是不是完整周。
            if (
                period == final_calendar_week
                and endpoint >= absolute_last
                and absolute_last.weekday() < 4
            ):
                continue
            selected.append((first_trade, last_trade, identifier))
        if not selected:
            raise ValueError(f"{month} 的{lookback_months}个月窗口内没有完整自然周")
        windows.append(
            WindowSpec(
                month=month,
                endpoint=endpoint,
                raw_start=raw_start,
                first_week_start=selected[0][0],
                last_week_end=selected[-1][1],
                week_ids=tuple(item[2] for item in selected),
            )
        )
    return windows


def _compound(values: np.ndarray) -> float:
    if values.size == 0 or not np.isfinite(values).all() or np.any(values <= -1.0):
        return math.nan
    return float(np.expm1(np.log1p(values).sum()))


def _score_factor(factor_name: str) -> dict[str, Any]:
    path = _SCORE_RETURN_ROOT / factor_name / "neutralization.parquet"
    if not path.is_file():
        return _result(
            factor_name,
            "skipped",
            reason="weekly_returns_missing",
            scores=[math.nan] * len(_SCORE_WINDOWS),
            directions=[""] * len(_SCORE_WINDOWS),
            week_counts=[0] * len(_SCORE_WINDOWS),
        )
    try:
        frame = read_weekly_output(path)
        frame["weekly_return"] = pd.to_numeric(
            frame["weekly_return"], errors="coerce"
        )
        series_by_direction: dict[str, pd.Series] = {}
        for direction in ("higher", "lower"):
            values = frame.loc[frame["direction"].eq(direction)].drop_duplicates(
                "week_id", keep="last"
            )
            series_by_direction[direction] = values.set_index("week_id")[
                "weekly_return"
            ]

        scores: list[float] = []
        directions: list[str] = []
        week_counts: list[int] = []
        for window in _SCORE_WINDOWS:
            candidates: list[tuple[float, int, str]] = []
            for direction_order, direction in enumerate(("higher", "lower")):
                values = series_by_direction[direction].reindex(window.week_ids)
                array = values.to_numpy(dtype="float64")
                finite_count = int(np.isfinite(array).sum())
                # 所有因子必须使用完全相同的自然周，避免缺周因子获得比较优势。
                if finite_count != len(window.week_ids):
                    continue
                score = _compound(array)
                if math.isfinite(score):
                    candidates.append((score, direction_order, direction))
            if not candidates:
                scores.append(math.nan)
                directions.append("")
                week_counts.append(0)
                continue
            candidates.sort(key=lambda item: (-item[0], item[1]))
            score, _, direction = candidates[0]
            scores.append(score)
            directions.append(direction)
            week_counts.append(len(window.week_ids))
        return _result(
            factor_name,
            "completed",
            scores=scores,
            directions=directions,
            week_counts=week_counts,
        )
    except Exception:
        return _result(
            factor_name,
            "failed",
            traceback=traceback.format_exc(),
        )


def _score_all_factors(
    factor_names: list[str],
    return_root: Path,
    windows: list[WindowSpec],
    workers: int,
) -> list[dict[str, Any]]:
    global _SCORE_RETURN_ROOT, _SCORE_WINDOWS
    _SCORE_RETURN_ROOT = return_root
    _SCORE_WINDOWS = tuple(windows)
    context = mp.get_context("fork")
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    with ProcessPoolExecutor(
        max_workers=min(max(1, workers), len(factor_names)),
        mp_context=context,
    ) as executor:
        futures = {
            executor.submit(_score_factor, factor_name): factor_name
            for factor_name in factor_names
        }
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="读取周收益并聚合全部月度窗口",
            unit="factor",
        ):
            result = future.result()
            results.append(result)
            if result["status"] == "failed":
                failures.append(result)
                tqdm.write(
                    f"FAILED {result['factor']}\n{result.get('traceback', '')}"
                )
    if failures:
        raise RuntimeError(f"周收益聚合失败: {len(failures)}")
    return sorted(results, key=lambda item: str(item["factor"]))


def _window_scores(
    results: list[dict[str, Any]],
    position: int,
    factor_to_category: dict[str, str],
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for result in results:
        if result["status"] != "completed":
            continue
        score = float(result["scores"][position])
        direction = str(result["directions"][position])
        if not math.isfinite(score) or direction not in {"higher", "lower"}:
            continue
        factor_name = str(result["factor"])
        records.append(
            {
                "factor_name": factor_name,
                "category_cn": factor_to_category[factor_name],
                "category_en": CATEGORY_ENGLISH[factor_to_category[factor_name]],
                "direction": direction,
                "direction_multiplier": 1.0 if direction == "higher" else -1.0,
                "window_compounded_return": score,
                "week_count": int(result["week_counts"][position]),
            }
        )
    scores = pd.DataFrame.from_records(records)
    if scores.empty:
        raise ValueError("当前窗口没有可用因子收益")
    return scores.sort_values(
        ["category_cn", "window_compounded_return", "factor_name"],
        ascending=[True, False, True],
        kind="mergesort",
    ).reset_index(drop=True)


def _return_select_diversified_winners(
    scores: pd.DataFrame,
    category_names: list[str],
    window: WindowSpec,
    window_label: str,
    lookback_months: int,
    selections_per_category: int,
    max_abs_correlation: float,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for category_name in category_names:
        candidates = scores.loc[scores["category_cn"].eq(category_name)]
        if candidates.empty:
            raise ValueError(f"类别{category_name}没有可用的周收益候选")
        chosen: list[str] = []
        for winner in candidates.itertuples(index=False):
            correlations = [
                _mean_window_abs_spearman(
                    str(winner.factor_name),
                    other,
                    window.first_week_start,
                    window.last_week_end,
                )
                for other in chosen
            ]
            if any(
                not np.isfinite(value) or value >= max_abs_correlation
                for value in correlations
            ):
                continue
            factor_name = str(winner.factor_name)
            chosen.append(factor_name)
            records.append({
                "selection_date": window.endpoint.strftime("%Y-%m-%d"),
                "target_month": str(window.target_month),
                "lookback_window": window_label,
                "lookback_months": lookback_months,
                "lookback_years": lookback_months / 12,
                "raw_window_start": window.raw_start.strftime("%Y-%m-%d"),
                "complete_week_start": window.first_week_start.strftime("%Y-%m-%d"),
                "complete_week_end": window.last_week_end.strftime("%Y-%m-%d"),
                "expected_week_count": len(window.week_ids),
                "category_cn": category_name,
                "category_en": CATEGORY_ENGLISH[category_name],
                "selection_rank": len(chosen),
                "factor_name": factor_name,
                "direction": str(winner.direction),
                "direction_multiplier": float(winner.direction_multiplier),
                "window_compounded_return": float(winner.window_compounded_return),
                "week_count": int(winner.week_count),
                "max_abs_correlation_to_earlier_selected": (
                    max(correlations) if correlations else 0.0
                ),
            })
            if len(chosen) == selections_per_category:
                break
        if len(chosen) != selections_per_category:
            raise ValueError(
                f"类别{category_name}只能选出{len(chosen)}个低相关收益因子"
            )
    return pd.DataFrame.from_records(records)


def _atomic_json(payload: dict[str, Any], path: Path) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(portable_payload(payload), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _window_ready(
    window_root: Path,
    category_names: list[str],
    selections_per_category: int,
) -> bool:
    required = [
        window_root / "return_scores.parquet",
        window_root / "selected_factors.parquet",
        window_root / "selection_metadata.json",
    ]
    if not all(path.is_file() for path in required):
        return False
    try:
        selected = pd.read_parquet(window_root / "selected_factors.parquet")
        if len(selected) != len(category_names) * selections_per_category:
            return False
        if set(selected["category_cn"]) != set(category_names):
            return False
        expected_ranks = set(range(1, selections_per_category + 1))
        for category_name in category_names:
            actual_ranks = set(
                pd.to_numeric(
                    selected.loc[
                        selected["category_cn"].eq(category_name),
                        "selection_rank",
                    ],
                    errors="raise",
                ).astype(int)
            )
            if actual_ranks != expected_ranks:
                return False
        factor_names = set(selected["factor_name"].astype(str))
        factor_dirs = {
            path.parent.name
            for path in window_root.glob("*/raw.parquet")
            if path.is_file()
        }
        return factor_dirs == factor_names
    except Exception:
        return False


def _materialize_window(
    *,
    window_root: Path,
    scores: pd.DataFrame,
    selected: pd.DataFrame,
    window: WindowSpec,
    window_label: str,
    lookback_months: int,
    start: str,
    workers: int,
    resume: bool,
    selections_per_category: int,
    max_abs_correlation: float,
    available_factor_count: int,
    skipped_factor_count: int,
) -> None:
    if resume and _window_ready(
        window_root,
        list(CATEGORY_ENGLISH),
        selections_per_category,
    ):
        print(f"WINDOW_SKIPPED_READY output={window_root}", flush=True)
        return
    _prepare_window_directory(window_root, resume)
    write_output_parquet(scores, window_root / "return_scores.parquet")
    write_output_parquet(selected, window_root / "selected_factors.parquet")
    _atomic_json(
        {
            "selection_date": window.endpoint.strftime("%Y-%m-%d"),
            "target_month": str(window.target_month),
            "lookback_window": window_label,
            "lookback_months": lookback_months,
            "lookback_years": lookback_months / 12,
            "raw_window_start": window.raw_start.strftime("%Y-%m-%d"),
            "complete_week_start": window.first_week_start.strftime("%Y-%m-%d"),
            "complete_week_end": window.last_week_end.strftime("%Y-%m-%d"),
            "expected_week_count": len(window.week_ids),
            "score": "compounded net weekly return",
            "direction_policy": "choose better of higher/lower per factor",
            "selections_per_category": selections_per_category,
            "correlation_metric": "absolute mean daily cross-sectional Spearman",
            "max_abs_correlation": max_abs_correlation,
            "available_factor_count": available_factor_count,
            "skipped_factor_count": skipped_factor_count,
            "factor_value_month_assignment": "available_date",
        },
        window_root / "selection_metadata.json",
    )
    winner_names = sorted(set(selected["factor_name"].astype(str)))
    tasks = [
        (name, start, window.endpoint.strftime("%Y-%m-%d"), str(window_root))
        for name in winner_names
    ]
    _run_parallel_collect(
        _materialize_filled_factor,
        tasks,
        min(max(1, workers), len(tasks)),
        f"{window.month} 十类胜出因子值复制",
    )
    print(
        f"WINDOW_DONE endpoint={window.endpoint:%Y-%m-%d} "
        f"target_month={window.target_month} winners={len(winner_names)} "
        f"output={window_root}",
        flush=True,
    )


def _build_live_schedule(
    selections: list[pd.DataFrame],
    windows: list[WindowSpec],
    final_month: str,
    selections_per_category: int,
) -> pd.DataFrame:
    final_period = pd.Period(final_month, freq="M")
    records: list[dict[str, Any]] = []
    for selected, window in zip(selections, windows, strict=True):
        target_month = window.target_month
        if target_month > final_period:
            continue
        for winner in selected.itertuples(index=False):
            selection_rank = int(winner.selection_rank)
            final_factor_name = (
                str(winner.category_en)
                if selections_per_category == 1
                else f"{winner.category_en}_{selection_rank}"
            )
            records.append(
                {
                    "target_period": str(target_month),
                    "target_start": target_month.start_time.normalize(),
                    "target_end": target_month.end_time.normalize(),
                    "selection_window": window.directory_name,
                    "selection_date": window.endpoint,
                    "complete_week_start": window.first_week_start,
                    "complete_week_end": window.last_week_end,
                    "category_cn": str(winner.category_cn),
                    "category_en": final_factor_name,
                    "base_category_en": str(winner.category_en),
                    "selection_rank": selection_rank,
                    "source_factor": str(winner.factor_name),
                    "direction": str(winner.direction),
                    "direction_multiplier": float(winner.direction_multiplier),
                    "selected_window_compounded_return": float(
                        winner.window_compounded_return
                    ),
                    "value_source": "full_value_library_read_only",
                }
            )
    schedule = pd.DataFrame.from_records(records)
    if schedule.empty:
        raise ValueError("没有可拼接的目标月份；final-month必须晚于first-month")
    expected_months = list(
        pd.period_range(windows[0].target_month, final_period, freq="M")
    )
    actual_months = sorted(
        pd.Period(value, freq="M") for value in schedule["target_period"].unique()
    )
    if actual_months != expected_months:
        raise ValueError("最终拼接月份不连续")
    expected_rows = (
        len(expected_months)
        * len(CATEGORY_ENGLISH)
        * selections_per_category
    )
    if len(schedule) != expected_rows:
        raise ValueError(
            f"最终拼接计划预期{expected_rows}行，实际{len(schedule)}行"
        )
    return schedule


def _merge_category_available_date(task: tuple[Any, ...]) -> dict[str, Any]:
    (
        category_cn,
        category_en,
        records,
        source_root_text,
        final_root_text,
    ) = task
    source_root = Path(source_root_text)
    final_root = Path(final_root_text)
    destination = final_root / str(category_en) / "factors"
    try:
        destination.mkdir(parents=True)
        source_dirs = {
            source_root / str(record["source_factor"])
            for record in records
        }
        missing = [str(path) for path in source_dirs if not path.is_dir()]
        if missing:
            raise FileNotFoundError(f"来源因子目录不存在: {missing[:5]}")
        symbols = sorted(
            {
                symbol
                for source_dir in source_dirs
                for symbol in _factor_symbols(source_dir)
            }
            | set(_EXPECTED_AVAILABLE_DATES_BY_SYMBOL)
        )
        raw_output = f"{category_en}_raw"
        neutral_output = f"{category_en}_neutralization"
        files = 0
        rows = 0
        constituent_rows_added = 0
        forward_filled_cells = 0
        median_parts: list[pd.DataFrame] = []
        for symbol in symbols:
            cache: dict[str, pd.DataFrame | None] = {}
            pieces: list[pd.DataFrame] = []
            for record in records:
                factor_name = str(record["source_factor"])
                if factor_name not in cache:
                    frame = _read_factor_stock(source_root / factor_name, factor_name, symbol)
                    if frame is None:
                        cache[factor_name] = None
                    else:
                        raw_source = f"{factor_name}_raw"
                        neutral_source = f"{factor_name}_neutralization"
                        frame["signal_date"] = pd.to_datetime(
                            frame["signal_date"], errors="raise"
                        )
                        frame["available_date"] = pd.to_datetime(
                            frame["available_date"], errors="coerce"
                        )
                        frame = frame.sort_values(
                            ["available_date", "signal_date"],
                            kind="mergesort",
                        )
                        # 只使用同一股票、同一源因子在T日以前最近的非空值；
                        # 先在完整历史上前向填充，再截取目标月，避免月初空值。
                        for column in (raw_source, neutral_source):
                            values = pd.to_numeric(
                                frame[column], errors="coerce"
                            ).replace([np.inf, -np.inf], np.nan)
                            missing_before = values.isna()
                            filled = pd.Series(_fill_selected_series(frame, symbol, values, float("nan")), index=values.index)
                            forward_filled_cells += int(
                                (missing_before & filled.notna()).sum()
                            )
                            frame[column] = filled
                        cache[factor_name] = frame
                source = cache[factor_name]
                if source is None:
                    continue
                start = pd.Timestamp(record["target_start"])
                end = pd.Timestamp(record["target_end"])
                # 因子身份按真正可用于交易的日期归属目标月。
                piece = source.loc[source["available_date"].between(start, end)].copy()
                if piece.empty:
                    continue
                multiplier = float(record["direction_multiplier"])
                if multiplier not in {-1.0, 1.0}:
                    raise ValueError(f"方向乘数非法: {multiplier}")
                raw_source = f"{factor_name}_raw"
                neutral_source = f"{factor_name}_neutralization"
                piece[raw_output] = (
                    pd.to_numeric(piece[raw_source], errors="coerce") * multiplier
                )
                piece[neutral_output] = (
                    pd.to_numeric(piece[neutral_source], errors="coerce") * multiplier
                )
                pieces.append(
                    piece[
                        [
                            "signal_date",
                            "available_date",
                            raw_output,
                            neutral_output,
                        ]
                    ]
                )
            expected_dates = pd.DatetimeIndex(
                _EXPECTED_AVAILABLE_DATES_BY_SYMBOL.get(symbol, ())
            )
            if pieces:
                merged = pd.concat(pieces, ignore_index=True).sort_values(
                    ["available_date", "signal_date"], kind="mergesort"
                )
            elif len(expected_dates):
                merged = pd.DataFrame(
                    columns=[
                        "signal_date",
                        "available_date",
                        raw_output,
                        neutral_output,
                    ]
                )
            else:
                continue
            if merged["available_date"].isna().any():
                raise ValueError(f"{category_en}/{symbol} 出现空available_date")
            if merged["available_date"].duplicated().any():
                raise ValueError(f"{category_en}/{symbol} 出现重复available_date")
            missing_dates = expected_dates.difference(
                pd.DatetimeIndex(merged["available_date"])
            )
            if len(missing_dates):
                missing_signal_dates = [
                    _AVAILABLE_TO_SIGNAL_DATE.get(pd.Timestamp(value))
                    for value in missing_dates
                ]
                if any(value is None for value in missing_signal_dates):
                    raise ValueError(
                        f"{category_en}/{symbol} 的缺失成分日期无法映射signal_date"
                    )
                additions = pd.DataFrame(
                    {
                        "signal_date": missing_signal_dates,
                        "available_date": missing_dates,
                        raw_output: np.nan,
                        neutral_output: np.nan,
                    }
                )
                if merged.empty:
                    merged = additions
                else:
                    merged = pd.concat(
                        [merged, additions], ignore_index=True
                    ).sort_values(
                        ["available_date", "signal_date"], kind="mergesort"
                    )
                constituent_rows_added += len(additions)
            merged = merged.loc[_member_rows(merged, symbol)].copy()
            median_part = merged[
                ["available_date", raw_output, neutral_output]
            ].copy()
            if median_part[[raw_output, neutral_output]].notna().any().any():
                median_parts.append(median_part)
            portable_frame(merged).to_parquet(
                destination / f"{symbol}.parquet",
                index=False,
            )
            files += 1
            rows += len(merged)
        if files == 0:
            raise ValueError(f"类别{category_cn}没有生成任何最终因子值")

        # 股票自身历史开头的预热型空缺无法用前向填充解决。这里仅使用同一
        # available_date 已经可得的其他股票因子值计算截面中位数，不读取
        # 未来日期。若某日整个截面都无有效值，则拒绝输出。
        if not median_parts:
            raise ValueError(f"类别{category_cn}整个区间没有可用于补齐的有效值")
        median_frame = pd.concat(median_parts, ignore_index=True)
        date_medians = median_frame.groupby("available_date", sort=False)[
            [raw_output, neutral_output]
        ].median()
        invalid_dates = date_medians.index[
            date_medians[[raw_output, neutral_output]].isna().any(axis=1)
        ]
        if len(invalid_dates):
            samples = [
                pd.Timestamp(value).strftime("%Y-%m-%d")
                for value in invalid_dates[:5]
            ]
            raise ValueError(
                f"{category_en} 有{len(invalid_dates)}个日期的全截面无有效值，"
                f"无法无泄露补齐: {samples}"
            )
        del median_parts, median_frame

        cross_sectional_filled_cells = 0
        remaining_missing_cells = 0
        for path in sorted(destination.glob("*.parquet")):
            frame = pd.read_parquet(path)
            changed = False
            for column in (raw_output, neutral_output):
                values = pd.to_numeric(frame[column], errors="coerce").replace(
                    [np.inf, -np.inf], np.nan
                )
                missing_before = values.isna()
                if missing_before.any():
                    values = values.fillna(
                        frame["available_date"].map(date_medians[column])
                    )
                    filled_count = int((missing_before & values.notna()).sum())
                    cross_sectional_filled_cells += filled_count
                    frame[column] = values
                    changed = filled_count > 0 or changed
                remaining_missing_cells += int(values.isna().sum())
            if changed:
                portable_frame(frame).to_parquet(path, index=False)
        if remaining_missing_cells:
            raise ValueError(
                f"{category_en} 无泄露补齐后仍有"
                f"{remaining_missing_cells}个缺失单元"
            )
        _consolidate_factor_staging(destination.parent, str(category_en))
        return {
            "factor": str(category_en),
            "status": "completed",
            "files": files,
            "rows": rows,
            "constituent_rows_added": constituent_rows_added,
            "forward_filled_cells": forward_filled_cells,
            "cross_sectional_filled_cells": cross_sectional_filled_cells,
        }
    except Exception:
        return {
            "factor": str(category_en),
            "status": "failed",
            "traceback": traceback.format_exc(),
        }


def _return_build_final(
    *,
    output_root: Path,
    source_root: Path,
    schedule: pd.DataFrame,
    window_label: str,
    lookback_months: int,
    selections_per_category: int,
    max_abs_correlation: float,
    merge_workers: int,
    resume: bool,
    constituents: Path = legacy.WEEKLY_CONSTITUENTS,
) -> None:
    final_root = output_root / "final"
    if final_root.exists() and not resume:
        raise FileExistsError(f"最终目录已存在: {final_root}；续跑请加--resume")
    temporary = output_root / f".final.{uuid.uuid4().hex}.tmp"
    temporary.mkdir(parents=True)
    try:
        _initialize_final_constituent_grid(constituents, schedule)
        manifest = schedule.copy()
        write_output_parquet(manifest, temporary / "selection_schedule.parquet")
        _atomic_json(
            {
                "lookback_window": window_label,
                "lookback_months": lookback_months,
                "lookback_years": lookback_months / 12,
                "selections_per_category": selections_per_category,
                "correlation_metric": "absolute mean daily cross-sectional Spearman",
                "max_abs_correlation": max_abs_correlation,
                "selection_timing": "previous month end selects next month",
                "factor_value_month_assignment": "available_date",
                "missing_value_policy": (
                    "per-symbol historical forward fill, then same-available-date "
                    "cross-sectional median; no backward fill"
                ),
                "required_row_coverage": (
                    "every signal-date constituent mapped to available_date"
                ),
                "direction_policy": "higher=+1, lower=-1",
                "source_root": str(source_root),
                "first_target_month": str(schedule["target_period"].iloc[0]),
                "last_target_month": str(schedule["target_period"].iloc[-1]),
            },
            temporary / "final_metadata.json",
        )
        tasks: list[tuple[Any, ...]] = []
        for category_en, subset in schedule.groupby("category_en", sort=True):
            category_name = str(subset.iloc[0]["category_cn"])
            tasks.append(
                (
                    category_name,
                    str(category_en),
                    subset.to_dict(orient="records"),
                    str(source_root),
                    str(temporary),
                )
            )
        context = mp.get_context("fork")
        failures: list[dict[str, Any]] = []
        with ProcessPoolExecutor(
            max_workers=min(max(1, merge_workers), len(tasks)),
            mp_context=context,
        ) as executor:
            futures = {
                executor.submit(_merge_category_available_date, task): task[1]
                for task in tasks
            }
            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc="收益率胜出因子按月拼接",
                unit="category",
            ):
                result = future.result()
                if result["status"] == "failed":
                    failures.append(result)
                    tqdm.write(
                        f"FAILED {result['factor']}\n{result.get('traceback', '')}"
                    )
                else:
                    tqdm.write(
                        f"MERGE_DONE category={result['factor']} "
                        f"files={result['files']} rows={result['rows']} "
                        f"constituent_rows_added={result['constituent_rows_added']} "
                        f"forward_filled_cells={result['forward_filled_cells']} "
                        "cross_sectional_filled_cells="
                        f"{result['cross_sectional_filled_cells']}"
                    )
        if failures:
            raise RuntimeError(f"最终类别因子拼接失败: {len(failures)}")
        if final_root.exists():
            shutil.rmtree(final_root)
        temporary.replace(final_root)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(
        f"FINAL_DONE output={final_root} "
        f"category_factors={len(CATEGORY_ENGLISH) * selections_per_category}",
        flush=True,
    )


def run_return_pipeline(
    *,
    window: str,
    output_root: Path | None = None,
    return_root: Path = DEFAULT_RETURN_ROOT,
    source_root: Path = RETURN_DEFAULT_SOURCE_ROOT,
    expansion_factor_config: Path = legacy.DEFAULT_EXPANSION_FACTOR_CONFIG,
    base_factor_config: Path = legacy.DEFAULT_BASE_FACTOR_CONFIG,
    constituents: Path = legacy.WEEKLY_CONSTITUENTS,
    start: str = legacy.DEFAULT_START_DATE,
    first_month: str = RETURN_DEFAULT_FIRST_MONTH,
    final_month: str = RETURN_DEFAULT_FINAL_MONTH,
    workers: int = RETURN_DEFAULT_WORKERS,
    merge_workers: int = RETURN_DEFAULT_MERGE_WORKERS,
    selections_per_category: int = RETURN_DEFAULT_SELECTIONS_PER_CATEGORY,
    max_abs_correlation: float = RETURN_DEFAULT_MAX_ABS_CORRELATION,
    resume: bool = False,
    plan_only: bool = False,
    skip_final: bool = False,
) -> None:
    global _IC_VERSION, _SOURCE_ROOT
    if window not in WINDOW_LOOKBACK_MONTHS:
        raise ValueError(f"window只能是{', '.join(WINDOW_LOOKBACK_MONTHS)}")
    if selections_per_category < 1:
        raise ValueError("selections_per_category必须大于等于1")
    if not 0 <= max_abs_correlation < 1:
        raise ValueError("max_abs_correlation必须在[0, 1)内")
    window_label = window
    lookback_months = WINDOW_LOOKBACK_MONTHS[window_label]
    if output_root is None:
        output_root = PROJECT_ROOT / f"outputs_new_return_{window_label}" / "zz500"
    output_root = output_root.resolve()
    return_root = return_root.resolve()
    source_root = source_root.resolve()
    _assert_source_is_read_only_scope(source_root, output_root)
    if not return_root.is_dir():
        raise FileNotFoundError(f"周收益目录不存在: {return_root}")
    if output_root == return_root or return_root in output_root.parents:
        raise ValueError("输出目录不能位于只读周收益目录内部")

    configs = _load_configs(expansion_factor_config, base_factor_config)
    factor_names = sorted(configs)
    category_names, factor_to_category = _load_categories(
        configs, set(factor_names)
    )
    if category_names != list(CATEGORY_ENGLISH):
        raise ValueError(f"十类顺序或名称不符合预期: {category_names}")
    _validate_source_factor_dirs(source_root, factor_names)
    calendar = _load_full_calendar(constituents)
    correlation_calendar = calendar[
        (calendar >= pd.Timestamp(start))
        & (calendar <= pd.Period(final_month, freq="M").end_time.normalize())
    ]
    if correlation_calendar.empty:
        raise ValueError("相关性计算交易日历为空")
    legacy._PIPELINE_DATES = correlation_calendar
    windows = _build_windows(
        calendar, first_month, final_month, lookback_months
    )
    available_count = sum(
        (return_root / name / "neutralization.parquet").is_file()
        for name in factor_names
    )
    skipped_count = len(factor_names) - available_count
    print(
        f"RETURN_SELECTION_PLAN window={window_label} lookback_months={lookback_months} "
        f"factors={len(factor_names)} available={available_count} "
        f"skipped={skipped_count} windows={len(windows)} "
        f"selections_per_category={selections_per_category} "
        f"max_abs_correlation={max_abs_correlation} output={output_root}",
        flush=True,
    )
    for window_spec in windows:
        print(
            f"{window_spec.month} endpoint={window_spec.endpoint:%Y-%m-%d} "
            f"target_month={window_spec.target_month} "
            f"complete_weeks={len(window_spec.week_ids)} "
            f"week_start={window_spec.first_week_start:%Y-%m-%d} "
            f"week_end={window_spec.last_week_end:%Y-%m-%d}",
            flush=True,
        )
    if plan_only:
        return

    output_root.mkdir(parents=True, exist_ok=True)
    _SOURCE_ROOT = source_root
    _IC_VERSION = "neutralization"
    _FACTOR_VALUE_CACHE.clear()
    _PAIR_DAILY_CORRELATION_CACHE.clear()
    results = _score_all_factors(factor_names, return_root, windows, workers)
    skipped = pd.DataFrame(
        [
            {
                "factor_name": result["factor"],
                "status": result["status"],
                "reason": result.get("reason", ""),
            }
            for result in results
            if result["status"] != "completed"
        ]
    )
    write_output_parquet(skipped, output_root / "skipped_factors.parquet")

    selections: list[pd.DataFrame] = []
    all_selected: list[pd.DataFrame] = []
    for position, window_spec in enumerate(windows):
        scores = _window_scores(results, position, factor_to_category)
        selected = _return_select_diversified_winners(
            scores,
            category_names,
            window_spec,
            window_label=window_label,
            lookback_months=lookback_months,
            selections_per_category=selections_per_category,
            max_abs_correlation=max_abs_correlation,
        )
        selections.append(selected)
        all_selected.append(selected)
        _materialize_window(
            window_root=output_root / window_spec.directory_name,
            scores=scores,
            selected=selected,
            window=window_spec,
            window_label=window_label,
            lookback_months=lookback_months,
            start=start,
            workers=workers,
            resume=resume,
            selections_per_category=selections_per_category,
            max_abs_correlation=max_abs_correlation,
            available_factor_count=available_count,
            skipped_factor_count=skipped_count,
        )
    write_output_parquet(
        pd.concat(all_selected, ignore_index=True),
        output_root / "all_month_selected_factors.parquet",
    )
    if not skip_final:
        schedule = _build_live_schedule(
            selections,
            windows,
            final_month,
            selections_per_category,
        )
        _return_build_final(
            output_root=output_root,
            source_root=source_root,
            schedule=schedule,
            window_label=window_label,
            lookback_months=lookback_months,
            selections_per_category=selections_per_category,
            max_abs_correlation=max_abs_correlation,
            merge_workers=merge_workers,
            resume=resume,
            constituents=constituents,
        )
    print(
        f"RETURN_SELECTION_DONE window={window_label} "
        f"windows={len(windows)} output={output_root}",
        flush=True,
    )


def _build_return_rebuild_schedule(
    output_root: Path,
    final_month: pd.Period,
) -> pd.DataFrame:
    path = output_root / "all_month_selected_factors.parquet"
    selected = pd.read_parquet(path)
    required = {
        "selection_date",
        "target_month",
        "category_cn",
        "category_en",
        "factor_name",
        "direction",
        "direction_multiplier",
        "window_compounded_return",
    }
    missing = required.difference(selected.columns)
    if missing:
        raise ValueError(f"{path} 缺少字段: {sorted(missing)}")
    selected["target_period"] = selected["target_month"].astype(str)
    selected["target_month_period"] = pd.PeriodIndex(
        selected["target_period"], freq="M"
    )
    selected = selected.loc[
        selected["target_month_period"].le(final_month)
    ].copy()
    expected_months = list(pd.period_range("2020-01", final_month, freq="M"))
    actual_months = sorted(selected["target_month_period"].unique())
    if actual_months != expected_months:
        raise ValueError(
            f"目标月份不是2020-01至{final_month.strftime('%Y-%m')}的连续月份"
        )
    expected_categories = set(CATEGORY_ENGLISH.values())
    for month, subset in selected.groupby("target_month_period", sort=True):
        if (
            len(subset) != len(expected_categories)
            or set(subset["category_en"]) != expected_categories
        ):
            raise ValueError(f"{month} 未能提供十类各一个因子")
    selected["target_start"] = selected["target_month_period"].map(
        lambda value: value.start_time.normalize()
    )
    selected["target_end"] = selected["target_month_period"].map(
        lambda value: value.end_time.normalize()
    )
    selected["source_factor"] = selected["factor_name"].astype(str)
    selected["selection_rank"] = 1
    selected["selected_window_compounded_return"] = pd.to_numeric(
        selected["window_compounded_return"], errors="raise"
    )
    selected["value_source"] = "full_value_library_read_only"
    selected = selected.drop(columns=["target_month_period"])
    selected = selected.sort_values(
        ["target_start", "category_en"], kind="mergesort"
    ).reset_index(drop=True)
    if len(selected) != len(expected_months) * len(expected_categories):
        raise ValueError(f"最终拼接计划行数错误: {len(selected)}")
    return selected


def _audit_return_final(final_root: Path) -> pd.DataFrame:
    records = []
    for category_en in sorted(CATEGORY_ENGLISH.values()):
        factor_root = final_root / category_en
        paths = [factor_root / symbol for symbol in _factor_symbols(factor_root)]
        if not paths:
            raise ValueError(f"{factor_root} 没有Parquet")
        raw_column = f"{category_en}_raw"
        neutral_column = f"{category_en}_neutralization"
        missing_cells = 0
        infinite_cells = 0
        duplicate_available_dates = 0
        missing_signal_dates = 0
        missing_constituent_rows = 0
        rows = 0
        exact_date_complete = 0
        exact_date = pd.Timestamp("2023-06-16")
        path_by_symbol = {path.name: path for path in paths}
        expected_by_symbol = _EXPECTED_AVAILABLE_DATES_BY_SYMBOL
        for symbol in sorted(set(path_by_symbol) | set(expected_by_symbol)):
            path = path_by_symbol.get(symbol)
            expected_dates = pd.DatetimeIndex(expected_by_symbol.get(symbol, ()))
            if path is None:
                missing_constituent_rows += len(expected_dates)
                continue
            frame = _read_factor_stock(factor_root, category_en, symbol)
            frame = frame.loc[_member_rows(frame, symbol)].copy()
            rows += len(frame)
            values = frame[[raw_column, neutral_column]].apply(
                pd.to_numeric, errors="coerce"
            )
            missing_cells += int(values.isna().sum().sum())
            infinite_cells += int(np.isinf(values.to_numpy(dtype="float64")).sum())
            duplicate_available_dates += int(frame["available_date"].duplicated().sum())
            missing_signal_dates += int(frame["signal_date"].isna().sum())
            actual_dates = pd.DatetimeIndex(frame["available_date"].dropna())
            missing_constituent_rows += len(expected_dates.difference(actual_dates))
            if exact_date in expected_dates:
                exact = frame.loc[frame["available_date"].eq(exact_date)]
                if len(exact) == 1 and exact[[raw_column, neutral_column]].notna().all(axis=None):
                    exact_date_complete += 1
        record = {
            "category": category_en,
            "files": len(paths),
            "rows": rows,
            "missing_value_cells": missing_cells,
            "infinite_value_cells": infinite_cells,
            "duplicate_available_dates": duplicate_available_dates,
            "missing_signal_dates": missing_signal_dates,
            "missing_constituent_rows": missing_constituent_rows,
            "complete_constituents_2023_06_16": exact_date_complete,
        }
        records.append(record)
        invalid = sum(
            record[key]
            for key in (
                "missing_value_cells",
                "infinite_value_cells",
                "duplicate_available_dates",
                "missing_signal_dates",
                "missing_constituent_rows",
            )
        )
        if invalid:
            raise ValueError(f"{category_en} final审计失败: {record}")
    return pd.DataFrame.from_records(records)


def _build_unified_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--selection-mode",
        required=True,
        choices=("ic", "return"),
        help="筛选模式：ic=按信息系数，return=按周复利净收益。",
    )
    parser.add_argument(
        "--window",
        required=True,
        choices=("6m", "1y", "2y", "3y"),
        help="回看窗口。",
    )
    parser.add_argument("--expansion-factor-config", type=resolve_project_path, default=legacy.DEFAULT_EXPANSION_FACTOR_CONFIG)
    parser.add_argument("--base-factor-config", type=resolve_project_path, default=legacy.DEFAULT_BASE_FACTOR_CONFIG)
    parser.add_argument("--source-root", type=resolve_project_path, default=legacy.DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--ic-root", type=resolve_project_path, default=DEFAULT_IC_ROOT)
    parser.add_argument("--output-root", type=resolve_project_path)
    parser.add_argument("--return-root", type=resolve_project_path, default=PROJECT_ROOT / "outputs" / "zz500" / "factor_return")
    parser.add_argument(
        "--data-dir",
        type=resolve_project_path,
        default=legacy.DEFAULT_DATA_DIR,
        help="IC模式的 stock_day 年/月 Parquet 分区目录。",
    )
    parser.add_argument(
        "--constituents",
        type=resolve_project_path,
        default=legacy.WEEKLY_CONSTITUENTS,
    )
    parser.add_argument(
        "--constituent-index",
        default="000905.SH",
        help="IC模式的指数代码；中证1000使用000852.SH。",
    )
    parser.add_argument("--selection-report", type=resolve_project_path)
    parser.add_argument(
        "--start",
        default=legacy.DEFAULT_START_DATE,
        help="历史数据起点，必须覆盖首个回看窗口；不是 final 输出起点。",
    )
    parser.add_argument(
        "--first-month",
        default=DEFAULT_FIRST_MONTH,
        help="首个筛选月；最终因子值从其下一自然月开始。",
    )
    parser.add_argument(
        "--final-month",
        default=DEFAULT_FINAL_MONTH,
        help="最后筛选月；最终因子值到其下一自然月结束。",
    )
    parser.add_argument("--workers", type=int)
    parser.add_argument("--merge-workers", type=int, default=DEFAULT_MERGE_WORKERS)
    parser.add_argument("--selections-per-category", type=int)
    parser.add_argument("--max-abs-correlation", type=float)
    parser.add_argument(
        "--ic-version",
        choices=legacy.FACTOR_VERSIONS,
        default="neutralization",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--skip-final", action="store_true")
    parser.add_argument(
        "--merge-final-only",
        action="store_true",
        help="IC模式只从既有 after_* 窗口重建 final。",
    )
    parser.add_argument(
        "--rebuild-final-only",
        action="store_true",
        help="收益率模式只从 all_month_selected_factors.parquet 重建并审计 final；仅兼容每类1个因子的旧结果。",
    )
    return parser


def _run_unified(args: argparse.Namespace) -> None:
    global FULL_VALUE_ROOT, ROLLING_ROOT
    global _SELECTION_DATA_DIR, _SELECTION_CONSTITUENTS
    global _SELECTION_CONSTITUENT_INDEX
    _SELECTION_DATA_DIR = args.data_dir.resolve()
    _SELECTION_CONSTITUENTS = args.constituents.resolve()
    _SELECTION_CONSTITUENT_INDEX = args.constituent_index
    legacy._PIPELINE_UNIVERSE_NAME = {
        "000905.SH": "中证500",
        "000852.SH": "中证1000",
    }.get(args.constituent_index, args.constituent_index)
    if args.merge_final_only and args.rebuild_final_only:
        raise ValueError("--merge-final-only 与 --rebuild-final-only 不能同时使用")
    if args.selection_mode == "ic":
        if args.rebuild_final_only:
            raise ValueError("--rebuild-final-only 仅适用于 return 模式")
        workers = args.workers or DEFAULT_WORKERS
        selections = (
            args.selections_per_category
            if args.selections_per_category is not None
            else DEFAULT_SELECTIONS_PER_CATEGORY[args.window]
        )
        correlation = args.max_abs_correlation
        source_root = args.source_root.resolve()
        output_root = (
            args.output_root.resolve()
            if args.output_root is not None
            else (PROJECT_ROOT / f"factors_value_ic_{args.window}").resolve()
        )
        if args.merge_final_only:
            configs = _load_configs(args.expansion_factor_config, args.base_factor_config)
            if args.plan_only:
                ROLLING_ROOT = output_root
                FULL_VALUE_ROOT = source_root
                schedule = _build_schedule(
                    configs=configs,
                    require_window_reports=False,
                    selections_per_category=selections,
                    selection_first_month=args.first_month,
                    selection_final_month=args.final_month,
                )
                print(
                    f"IC_FINAL_PLAN rows={len(schedule)} output={output_root / 'final'}",
                    flush=True,
                )
                return
            _build_final(
                configs=configs,
                output_root=output_root,
                source_root=source_root,
                workers=workers,
                merge_workers=max(1, args.merge_workers),
                recent_days=WINDOW_TRADING_DAYS[args.window],
                selections_per_category=selections,
                max_abs_correlation=correlation,
                selection_first_month=args.first_month,
                selection_final_month=args.final_month,
            )
            return
        run_pipeline(
            window=args.window,
            expansion_config_path=args.expansion_factor_config,
            base_config_path=args.base_factor_config,
            source_root=source_root,
            ic_root=args.ic_root,
            output_root=output_root,
            selection_report_path=args.selection_report,
            start=args.start,
            first_month=args.first_month,
            final_month=args.final_month,
            workers=workers,
            merge_workers=max(1, args.merge_workers),
            resume=args.resume,
            ic_version=args.ic_version,
            plan_only=args.plan_only,
            data_dir=args.data_dir,
            constituents=args.constituents,
            constituent_index=args.constituent_index,
            selections_per_category=args.selections_per_category,
            max_abs_correlation=correlation,
        )
        return

    if args.merge_final_only:
        raise ValueError("--merge-final-only 仅适用于 ic 模式")
    workers = args.workers or RETURN_DEFAULT_WORKERS
    selections = (
        args.selections_per_category
        if args.selections_per_category is not None
        else RETURN_DEFAULT_SELECTIONS_PER_CATEGORY
    )
    correlation = (
        args.max_abs_correlation
        if args.max_abs_correlation is not None
        else RETURN_DEFAULT_MAX_ABS_CORRELATION
    )
    output_root = (
        args.output_root.resolve()
        if args.output_root is not None
        else (PROJECT_ROOT / f"outputs_new_return_{args.window}" / "zz500").resolve()
    )
    source_root = args.source_root.resolve()
    if args.rebuild_final_only:
        if selections != 1:
            raise ValueError("--rebuild-final-only 仅兼容 --selections-per-category 1")
        final_month = pd.Period(args.final_month, freq="M")
        schedule = _build_return_rebuild_schedule(output_root, final_month)
        if args.plan_only:
            print(
                f"RETURN_FINAL_PLAN rows={len(schedule)} output={output_root / 'final'}",
                flush=True,
            )
            return
        _return_build_final(
            output_root=output_root,
            source_root=source_root,
            schedule=schedule,
            window_label=args.window,
            lookback_months=WINDOW_LOOKBACK_MONTHS[args.window],
            selections_per_category=1,
            max_abs_correlation=correlation,
            merge_workers=max(1, args.merge_workers),
            resume=True,
            constituents=args.constituents.resolve(),
        )
        audit = _audit_return_final(output_root / "final")
        write_output_parquet(audit, output_root / "final" / "final_fill_audit.parquet")
        print(audit.to_string(index=False), flush=True)
        print(f"FINAL_AUDIT_OK output={output_root / 'final'}", flush=True)
        return
    run_return_pipeline(
        window=args.window,
        output_root=output_root,
        return_root=args.return_root.resolve(),
        source_root=source_root,
        expansion_factor_config=args.expansion_factor_config,
        base_factor_config=args.base_factor_config,
        constituents=args.constituents.resolve(),
        start=args.start,
        first_month=args.first_month,
        final_month=args.final_month,
        workers=workers,
        merge_workers=max(1, args.merge_workers),
        selections_per_category=selections,
        max_abs_correlation=correlation,
        resume=args.resume,
        plan_only=args.plan_only,
        skip_final=args.skip_final,
    )


def main(argv: list[str] | None = None) -> None:
    arguments = list(sys.argv[1:] if argv is None else argv)
    _run_unified(_build_unified_parser().parse_args(arguments))


if __name__ == "__main__":
    main()
