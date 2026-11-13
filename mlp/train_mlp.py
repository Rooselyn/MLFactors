#!/usr/bin/env python3
"""MLP v5增强版统一训练入口。

本文件内置八年滚动窗口、IC/收益混合选因子、逐日交叉拟合残差去噪、
五分组Softsign MLP和双RankNet损失，不依赖已删除的历史v3/v4/v5训练脚本。
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import sys
import threading
import time
from typing import Any
import uuid
import warnings

import numpy as np
import pandas as pd
import torch
from torch import nn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from dataloader import portable_payload, portable_frame, resolve_project_path

import factors_select
import run as legacy
from dataloader import read_weekly_output, write_output_parquet
from factors.inputs import FactorDataLoader
from factors_eval import calc_forward_returns

DEFAULT_SOURCE_ROOT = PROJECT_ROOT / "outputs" / "zz500" / "factor_value"
DEFAULT_IC_ROOT = PROJECT_ROOT / "outputs" / "zz500" / "factor_ic"
DEFAULT_RETURN_ROOT = PROJECT_ROOT / "outputs" / "zz500" / "factor_return"

HIDDEN_DIMS = (64, 32, 16)
NUM_GROUPS = 5
FORWARD_PERIOD = 5
FUTURE_PRICE_STEPS = FORWARD_PERIOD + 1
FIXED_EPOCHS = 6
OUTPUT_BOUND = 20.0
RETURN_TO_PERCENT_POINTS = 100.0
NEWEST_TO_OLDEST_WEIGHT = 2.0
CATEGORY_NAMES = factors_select.CATEGORY_NAMES
MODEL_INIT_LOCK = threading.Lock()

DEFAULT_DENOISE_STOCKS = 200
DEFAULT_DENOISE_FOLDS = 5
DEFAULT_DENOISE_RIDGE_ALPHA = 10.0
DEFAULT_DENOISE_DAY_BATCH = 32
DEFAULT_SPLINE_KNOT = 0.5
BASIS_PER_FACTOR = 3

DEFAULT_TOP20_BOTTOM80_WEIGHT = 1.0
DEFAULT_TOP20_BOTTOM20_WEIGHT = 1.0
GROUP_VALUES = np.arange(1, NUM_GROUPS + 1, dtype=np.float32)


@dataclass(frozen=True)
class Window:
    number: int
    total: int
    output_month: str
    endpoint: pd.Timestamp
    window_start: pd.Timestamp
    train_end: pd.Timestamp
    validation_start: pd.Timestamp
    factor_end: pd.Timestamp
    prediction_start: pd.Timestamp
    prediction_end: pd.Timestamp


def atomic_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(portable_payload(payload), ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)

def atomic_parquet(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    portable_frame(frame).to_parquet(temporary, index=False)
    os.replace(temporary, path)

def atomic_model(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    torch.save(portable_payload(payload), temporary)
    os.replace(temporary, path)

def scheduled_learning_rate(
    epoch: int, total_schedule_epochs: int, maximum: float, minimum: float
) -> float:
    if epoch == 1:
        return maximum
    progress = (epoch - 2) / max(1, total_schedule_epochs - 2)
    return minimum + 0.5 * (maximum - minimum) * (
        1.0 + math.cos(math.pi * progress)
    )

def clone_state(model: nn.Module) -> dict[str, torch.Tensor]:
    return {
        name: value.detach().cpu().clone()
        for name, value in model.state_dict().items()
    }

@dataclass(frozen=True)
class ICMatrixStore:
    factor_to_column: dict[str, int]
    dates: np.ndarray
    values: np.ndarray

    def weighted_mean(
        self, factor: str, start: pd.Timestamp, end: pd.Timestamp
    ) -> float:
        column = self.factor_to_column.get(factor)
        if column is None:
            return np.nan
        left = int(np.searchsorted(self.dates, start.to_datetime64(), side="left"))
        right = int(np.searchsorted(self.dates, end.to_datetime64(), side="right"))
        values = self.values[left:right, column].astype(np.float64, copy=False)
        finite = np.isfinite(values)
        values = values[finite]
        if not len(values):
            return np.nan
        weights = exponential_weights(len(values))
        return float(np.dot(weights, values) / weights.sum())

@dataclass(frozen=True)
class WeeklyReturnSeries:
    first_dates: np.ndarray
    last_dates: np.ndarray
    higher: np.ndarray
    lower: np.ndarray

    def weighted_compounded(
        self, start: pd.Timestamp, end: pd.Timestamp
    ) -> tuple[float, float]:
        usable = (self.first_dates >= start.to_datetime64()) & (
            self.last_dates <= end.to_datetime64()
        )
        higher = self.higher[usable]
        lower = self.lower[usable]
        if not len(higher):
            return np.nan, np.nan
        weights = exponential_weights(len(higher))
        # 令平均权重为 1，既保持最早:最新=1:2，也保持三年累计收益量纲。
        weights = weights / weights.mean()
        weighted_higher = math.expm1(float(np.dot(weights, np.log1p(higher))))
        weighted_lower = math.expm1(float(np.dot(weights, np.log1p(lower))))
        return weighted_higher, weighted_lower

@dataclass
class DailyRegressionPanel:
    features: np.ndarray
    targets: np.ndarray
    labels: np.ndarray
    valid: np.ndarray
    date_weights: np.ndarray
    dates: pd.DatetimeIndex

@dataclass
class DeviceRegressionPanel:
    features: torch.Tensor
    targets: torch.Tensor
    labels: torch.Tensor
    valid: torch.Tensor
    date_weights: torch.Tensor

def exponential_weights(length: int) -> np.ndarray:
    if length <= 0:
        return np.empty(0, dtype=np.float64)
    if length == 1:
        return np.ones(1, dtype=np.float64)
    u = np.linspace(0.0, 1.0, length, dtype=np.float64)
    return np.exp(math.log(NEWEST_TO_OLDEST_WEIGHT) * u)

def load_ic_matrix_store(
    ic_root: Path, factor_names: list[str], workers: int
) -> ICMatrixStore:
    """读取 outputs/zz500/factor_ic 下逐因子保存的日频中性化 IC。"""
    missing = [name for name in factor_names if not (ic_root / name / "neutralization.parquet").is_file()]
    if missing:
        raise FileNotFoundError(
            f"{ic_root}缺少{len(missing)}个因子IC文件，示例：{missing[:10]}"
        )

    def load_one(position: int, factor: str) -> tuple[int, np.ndarray, np.ndarray]:
        path = ic_root / factor / "neutralization.parquet"
        frame = pd.read_parquet(path, columns=["signal_date", "IC_neutralization"])
        if frame["signal_date"].isna().any():
            raise ValueError(f"IC文件含无效日期：{path}")
        if frame["signal_date"].duplicated().any():
            raise ValueError(f"IC文件含重复日期：{path}")
        frame = frame.sort_values("signal_date")
        dates = frame["signal_date"].to_numpy(dtype="datetime64[ns]")
        values = pd.to_numeric(
            frame["IC_neutralization"], errors="coerce"
        ).to_numpy(dtype=np.float32)
        return position, dates, values

    started = time.monotonic()
    dates: np.ndarray | None = None
    values: np.ndarray | None = None
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = [
            executor.submit(load_one, position, factor)
            for position, factor in enumerate(factor_names)
        ]
        for completed, future in enumerate(as_completed(futures), start=1):
            position, factor_dates, factor_values = future.result()
            if dates is None:
                dates = factor_dates
                values = np.full(
                    (len(dates), len(factor_names)), np.nan, dtype=np.float32
                )
            elif not np.array_equal(factor_dates, dates):
                raise ValueError(
                    f"IC日期序列不一致：{ic_root / factor_names[position] / 'neutralization.parquet'}"
                )
            values[:, position] = factor_values
            if completed % 500 == 0 or completed == len(futures):
                print(
                    f"IC_MATRIX_PROGRESS completed={completed}/{len(futures)}",
                    flush=True,
                )
    if dates is None or values is None or not len(dates):
        raise ValueError(f"{ic_root}中没有可用IC数据")
    print(
        f"IC_MATRIX_DONE dates={len(dates)} factors={len(factor_names)} "
        f"elapsed_seconds={time.monotonic() - started:.2f}",
        flush=True,
    )
    return ICMatrixStore(
        factor_to_column={
            factor: position for position, factor in enumerate(factor_names)
        },
        dates=dates,
        values=values,
    )

def load_weekly_return_series(path: Path) -> WeeklyReturnSeries | None:
    if not path.is_file():
        return None
    try:
        frame = read_weekly_output(path)
    except (ValueError, OSError):
        return None
    by_direction: dict[str, pd.DataFrame] = {}
    for direction in ("higher", "lower"):
        rows = frame.loc[frame["direction"].eq(direction)].copy()
        rows["weekly_return"] = pd.to_numeric(rows["weekly_return"], errors="coerce")
        rows = rows.drop_duplicates("week_last_trade", keep="last").sort_values(
            "week_last_trade"
        )
        if rows.empty or rows["weekly_return"].isna().any():
            return None
        if (rows["weekly_return"] <= -1.0).any():
            return None
        by_direction[direction] = rows.set_index("week_last_trade")
    common = by_direction["higher"].index.intersection(
        by_direction["lower"].index
    ).sort_values()
    if common.empty:
        return None
    higher_rows = by_direction["higher"].reindex(common)
    lower_rows = by_direction["lower"].reindex(common)
    return WeeklyReturnSeries(
        first_dates=higher_rows["week_first_trade"].to_numpy(dtype="datetime64[ns]"),
        last_dates=common.to_numpy(dtype="datetime64[ns]"),
        higher=higher_rows["weekly_return"].to_numpy(dtype=np.float64),
        lower=lower_rows["weekly_return"].to_numpy(dtype=np.float64),
    )

def preload_metric_stores(
    factor_names: list[str], ic_root: Path, return_root: Path, workers: int
) -> tuple[ICMatrixStore, dict[str, WeeklyReturnSeries]]:
    ic_store = load_ic_matrix_store(ic_root, factor_names, workers)
    return_store: dict[str, WeeklyReturnSeries] = {}

    def load_one(name: str) -> tuple[str, WeeklyReturnSeries | None]:
        returns = load_weekly_return_series(
            return_root / name / "neutralization.parquet"
        )
        return name, returns

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = [executor.submit(load_one, name) for name in factor_names]
        for position, future in enumerate(as_completed(futures), start=1):
            name, returns = future.result()
            if returns is not None:
                return_store[name] = returns
            if position % 500 == 0 or position == len(futures):
                print(
                    f"METRIC_STORE_PROGRESS completed={position}/{len(futures)} "
                    f"ic_usable={len(ic_store.factor_to_column)} "
                    f"return_usable={len(return_store)}",
                    flush=True,
                )
    print(
        f"METRIC_STORE_DONE ic_usable={len(ic_store.factor_to_column)} "
        f"return_usable={len(return_store)} "
        f"elapsed_seconds={time.monotonic() - started:.2f}",
        flush=True,
    )
    return ic_store, return_store

def make_quintile_labels(returns: np.ndarray) -> np.ndarray:
    values = np.asarray(returns, dtype=np.float64)
    labels = np.full(len(values), -1, dtype=np.int64)
    finite_positions = np.flatnonzero(np.isfinite(values))
    count = len(finite_positions)
    if count < NUM_GROUPS:
        return labels
    order = finite_positions[np.argsort(values[finite_positions], kind="mergesort")]
    # rank=0 为最低收益，rank=count-1 为最高收益。
    groups = np.minimum(
        NUM_GROUPS - 1,
        np.floor(NUM_GROUPS * np.arange(count, dtype=np.float64) / count).astype(
            np.int64
        ),
    )
    labels[order] = groups
    return labels

def panel_to_device(
    panel: DailyRegressionPanel, device: torch.device
) -> DeviceRegressionPanel:
    return DeviceRegressionPanel(
        features=torch.from_numpy(panel.features).to(device, non_blocking=True),
        targets=torch.from_numpy(panel.targets).to(device, non_blocking=True),
        labels=torch.from_numpy(panel.labels).to(device, non_blocking=True),
        valid=torch.from_numpy(panel.valid).to(device, non_blocking=True),
        date_weights=torch.from_numpy(panel.date_weights).to(device, non_blocking=True),
    )

def _preprocess_features(values: np.ndarray, dates: np.ndarray) -> np.ndarray:
    """逐日 MAD 去极值、截面标准化；NaN/Inf 最终仅在内存中填 0。"""
    output = np.asarray(values, dtype=np.float32).copy()
    output[~np.isfinite(output)] = np.nan
    if len(output) == 0:
        return np.ascontiguousarray(output)
    boundaries = np.r_[0, np.flatnonzero(dates[1:] != dates[:-1]) + 1, len(dates)]
    for start, end in zip(boundaries[:-1], boundaries[1:], strict=True):
        block = output[start:end]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            median = np.nanmedian(block, axis=0)
            mad = np.nanmedian(np.abs(block - median), axis=0)
        usable = np.isfinite(mad) & (mad > 1e-12)
        if usable.any():
            block[:, usable] = np.clip(
                block[:, usable],
                median[usable] - 5.0 * mad[usable],
                median[usable] + 5.0 * mad[usable],
            )
        finite = np.isfinite(block)
        count = finite.sum(axis=0)
        total = np.where(finite, block, 0.0).sum(axis=0, dtype=np.float64)
        mean = np.divide(total, count, out=np.zeros_like(total), where=count > 0)
        centered = np.where(finite, block - mean, 0.0)
        variance = np.divide(
            np.square(centered, dtype=np.float64).sum(axis=0),
            count,
            out=np.zeros_like(total),
            where=count > 0,
        )
        std = np.sqrt(variance)
        std[~np.isfinite(std) | (std <= 1e-12)] = 1.0
        block = (block - mean) / std
        block[~np.isfinite(block)] = 0.0
        output[start:end] = block.astype(np.float32, copy=False)
    output = np.nan_to_num(output, nan=0.0, posinf=0.0, neginf=0.0)
    return np.ascontiguousarray(output, dtype=np.float32)

def _window_index(
    market_index: pd.MultiIndex,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.MultiIndex:
    dates = market_index.get_level_values("date")
    return market_index[(dates >= start) & (dates <= end)]

def _make_prediction_grid(
    market_index: pd.MultiIndex,
    calendar: pd.DatetimeIndex,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> tuple[pd.MultiIndex, pd.DataFrame]:
    available_index = _window_index(market_index, start, end)
    if available_index.empty:
        raise ValueError(f"{start:%Y-%m-%d} 至 {end:%Y-%m-%d} 没有预测样本")
    available_dates = available_index.get_level_values("date")
    expected_dates = calendar[(calendar >= start) & (calendar <= end)]
    actual_dates = pd.DatetimeIndex(available_dates.unique()).sort_values()
    missing_dates = expected_dates.difference(actual_dates)
    if len(missing_dates):
        raise ValueError(
            "预测网格遗漏交易日: "
            + ",".join(date.strftime("%Y-%m-%d") for date in missing_dates)
        )
    previous: dict[pd.Timestamp, pd.Timestamp] = {}
    for date in actual_dates:
        position = calendar.get_loc(date)
        if not isinstance(position, (int, np.integer)) or position == 0:
            raise ValueError(f"{date:%Y-%m-%d} 缺少上一交易日")
        previous[pd.Timestamp(date)] = pd.Timestamp(calendar[position - 1])
    signal_dates = np.array(
        [previous[pd.Timestamp(date)] for date in available_dates],
        dtype="datetime64[ns]",
    )
    symbols = available_index.get_level_values("symbol").to_numpy()
    signal_index = pd.MultiIndex.from_arrays(
        [signal_dates, symbols], names=["date", "symbol"]
    )
    metadata = pd.DataFrame(
        {
            "signal_date": signal_dates,
            "available_date": available_dates.to_numpy(dtype="datetime64[ns]"),
            "symbol": symbols,
        }
    )
    return signal_index, metadata

@dataclass
class DenoisedPanelResult:
    panel: DailyRegressionPanel
    audit: pd.DataFrame
    selected_global_positions: np.ndarray
    selected_oof_absolute_residuals: np.ndarray

def stable_symbol_fold(symbol: str, folds: int) -> int:
    """Stable across processes and Python hash seeds."""
    digest = hashlib.blake2b(str(symbol).encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, byteorder="little", signed=False) % folds

def additive_spline_basis(features: torch.Tensor, knot: float) -> torch.Tensor:
    """Three factor-specific piecewise-linear terms; no cross-factor interactions."""
    return torch.cat(
        [
            features,
            torch.relu(features - knot),
            torch.relu(-features - knot),
        ],
        dim=-1,
    )

@torch.inference_mode()
def cross_fitted_daily_predictions(
    *,
    features: np.ndarray,
    targets: np.ndarray,
    valid: np.ndarray,
    folds: np.ndarray,
    device: torch.device,
    stream: torch.cuda.Stream | None,
    fold_count: int,
    ridge_alpha: float,
    day_batch: int,
    spline_knot: float,
) -> np.ndarray:
    """Fit one additive Ridge curve per day and return symbol-fold OOF values."""
    day_count, stock_count, factor_count = features.shape
    output = np.full((day_count, stock_count), np.nan, dtype=np.float32)
    regularizer = torch.full(
        (1 + BASIS_PER_FACTOR * factor_count,),
        float(ridge_alpha),
        dtype=torch.float32,
        device=device,
    )
    # A tiny intercept penalty makes the batched solve well-defined in edge cases.
    regularizer[0] = 1e-6

    def run_batches() -> None:
        for day_start in range(0, day_count, day_batch):
            day_end = min(day_start + day_batch, day_count)
            x = torch.from_numpy(features[day_start:day_end]).to(
                device, non_blocking=True
            )
            y = torch.from_numpy(targets[day_start:day_end]).to(
                device, non_blocking=True
            )
            is_valid = torch.from_numpy(valid[day_start:day_end]).to(
                device, non_blocking=True
            )
            fold_ids = torch.from_numpy(folds[day_start:day_end]).to(
                device, non_blocking=True
            )
            basis = additive_spline_basis(x.float(), spline_knot)
            intercept = torch.ones(
                (*basis.shape[:-1], 1), dtype=torch.float32, device=device
            )
            design = torch.cat([intercept, basis], dim=-1)
            predictions = torch.full_like(y, torch.nan, dtype=torch.float32)
            for held_out_fold in range(fold_count):
                train_mask = is_valid & fold_ids.ne(held_out_fold)
                test_mask = is_valid & fold_ids.eq(held_out_fold)
                weighted_design = design * train_mask.unsqueeze(-1)
                xtx = design.transpose(1, 2).bmm(weighted_design)
                xty = design.transpose(1, 2).bmm(
                    (y * train_mask).unsqueeze(-1)
                ).squeeze(-1)
                system = xtx + torch.diag(regularizer).unsqueeze(0)
                coefficients = torch.linalg.solve(system, xty.unsqueeze(-1)).squeeze(-1)
                fold_prediction = design.bmm(coefficients.unsqueeze(-1)).squeeze(-1)
                predictions = torch.where(test_mask, fold_prediction, predictions)
            output[day_start:day_end] = predictions.cpu().numpy()

    if device.type == "cuda":
        if stream is None:
            raise ValueError("CUDA去噪必须传入独立stream")
        with torch.cuda.stream(stream):
            run_batches()
            stream.synchronize()
    else:
        run_batches()
    if not np.isfinite(output[valid]).all():
        raise FloatingPointError("每日交叉拟合产生NaN或Inf")
    return output

def balanced_smallest_residual_positions(
    labels: np.ndarray,
    residuals: np.ndarray,
    global_positions: np.ndarray,
    target_count: int,
) -> np.ndarray:
    """Keep equal realised-return-quintile quotas, then fill any shortfall."""
    candidate = np.flatnonzero(
        (labels >= 0) & np.isfinite(residuals) & (global_positions >= 0)
    )
    keep_count = min(target_count, len(candidate))
    if keep_count == 0:
        return np.empty(0, dtype=np.int64)
    base, remainder = divmod(keep_count, NUM_GROUPS)
    selected: list[int] = []
    # Give an unavoidable remainder to high-return groups first; at 200 this is 0.
    quotas = np.full(NUM_GROUPS, base, dtype=np.int64)
    if remainder:
        quotas[np.arange(NUM_GROUPS - 1, -1, -1)[:remainder]] += 1
    for group in range(NUM_GROUPS):
        members = candidate[labels[candidate] == group]
        order = np.lexsort((global_positions[members], residuals[members]))
        selected.extend(members[order[: quotas[group]]].tolist())
    if len(selected) < keep_count:
        chosen = np.zeros(len(labels), dtype=bool)
        chosen[np.asarray(selected, dtype=np.int64)] = True
        remaining = candidate[~chosen[candidate]]
        order = np.lexsort((global_positions[remaining], residuals[remaining]))
        selected.extend(remaining[order[: keep_count - len(selected)]].tolist())
    result = np.asarray(selected, dtype=np.int64)
    order = np.lexsort((global_positions[result], residuals[result]))
    return result[order]

def build_denoised_daily_panel(
    *,
    features: np.ndarray,
    returns: pd.Series,
    index: pd.MultiIndex,
    device: torch.device,
    stream: torch.cuda.Stream | None,
    target_stocks: int,
    fold_count: int,
    ridge_alpha: float,
    day_batch: int,
    spline_knot: float,
) -> DenoisedPanelResult:
    """Independently select the lowest-OOF-residual stocks on every date."""
    if len(features) != len(index):
        raise ValueError("features与index长度不一致")
    dates = pd.DatetimeIndex(index.get_level_values("date"))
    symbols = index.get_level_values("symbol").astype(str).to_numpy()
    date_values = dates.to_numpy(dtype="datetime64[ns]")
    boundaries = np.r_[
        0,
        np.flatnonzero(date_values[1:] != date_values[:-1]) + 1,
        len(date_values),
    ]
    raw_returns = returns.reindex(index).to_numpy(dtype=np.float64)
    target_values = np.clip(
        raw_returns * RETURN_TO_PERCENT_POINTS,
        -OUTPUT_BOUND,
        OUTPUT_BOUND,
    )
    day_records: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []
    kept_dates: list[pd.Timestamp] = []
    max_stock_count = 0
    for start, end in zip(boundaries[:-1], boundaries[1:], strict=True):
        positions = np.arange(start, end, dtype=np.int64)
        labels = make_quintile_labels(target_values[positions])
        usable = labels >= 0
        positions = positions[usable]
        labels = labels[usable]
        if len(np.unique(labels)) != NUM_GROUPS:
            continue
        targets = target_values[positions].astype(np.float32)
        fold_ids = np.fromiter(
            (stable_symbol_fold(symbols[pos], fold_count) for pos in positions),
            dtype=np.int64,
            count=len(positions),
        )
        if len(np.unique(fold_ids)) != fold_count:
            raise ValueError(f"{date_values[start]}未覆盖全部{fold_count}个symbol折")
        day_records.append((positions, targets, labels, fold_ids))
        kept_dates.append(pd.Timestamp(date_values[start]))
        max_stock_count = max(max_stock_count, len(positions))
    if not day_records:
        raise ValueError("没有可用于v4每日去噪的横截面")

    day_count = len(day_records)
    padded_x = np.zeros(
        (day_count, max_stock_count, features.shape[1]), dtype=np.float32
    )
    padded_y = np.zeros((day_count, max_stock_count), dtype=np.float32)
    padded_labels = np.full((day_count, max_stock_count), -1, dtype=np.int64)
    padded_valid = np.zeros((day_count, max_stock_count), dtype=bool)
    padded_folds = np.full((day_count, max_stock_count), -1, dtype=np.int64)
    global_positions = np.full((day_count, max_stock_count), -1, dtype=np.int64)
    for row, (positions, targets, labels, fold_ids) in enumerate(day_records):
        count = len(positions)
        padded_x[row, :count] = features[positions]
        padded_y[row, :count] = targets
        padded_labels[row, :count] = labels
        padded_valid[row, :count] = True
        padded_folds[row, :count] = fold_ids
        global_positions[row, :count] = positions

    oof_predictions = cross_fitted_daily_predictions(
        features=padded_x,
        targets=padded_y,
        valid=padded_valid,
        folds=padded_folds,
        device=device,
        stream=stream,
        fold_count=fold_count,
        ridge_alpha=ridge_alpha,
        day_batch=day_batch,
        spline_knot=spline_knot,
    )
    absolute_residuals = np.abs(oof_predictions - padded_y)
    max_selected = min(target_stocks, max(len(item[0]) for item in day_records))
    selected_x = np.zeros(
        (day_count, max_selected, features.shape[1]), dtype=np.float32
    )
    selected_y = np.zeros((day_count, max_selected), dtype=np.float32)
    selected_labels = np.full((day_count, max_selected), -1, dtype=np.int64)
    selected_valid = np.zeros((day_count, max_selected), dtype=bool)
    selected_global = np.full((day_count, max_selected), -1, dtype=np.int64)
    selected_residual = np.full((day_count, max_selected), np.nan, dtype=np.float32)
    audit_rows: list[dict[str, Any]] = []

    for day in range(day_count):
        chosen = balanced_smallest_residual_positions(
            padded_labels[day],
            absolute_residuals[day],
            global_positions[day],
            target_stocks,
        )
        count = len(chosen)
        chosen_global = global_positions[day, chosen]
        selected_x[day, :count] = padded_x[day, chosen]
        selected_y[day, :count] = padded_y[day, chosen]
        selected_labels[day, :count] = padded_labels[day, chosen]
        selected_valid[day, :count] = True
        selected_global[day, :count] = chosen_global
        selected_residual[day, :count] = absolute_residuals[day, chosen]
        all_valid = padded_valid[day]
        all_y = padded_y[day, all_valid].astype(np.float64)
        all_pred = oof_predictions[day, all_valid].astype(np.float64)
        all_residual = absolute_residuals[day, all_valid].astype(np.float64)
        selected_day_residual = absolute_residuals[day, chosen].astype(np.float64)
        unselected = all_valid.copy()
        unselected[chosen] = False
        denominator = np.square(all_y - all_y.mean()).sum()
        r2 = (
            1.0 - np.square(all_y - all_pred).sum() / denominator
            if denominator > 0
            else np.nan
        )
        record: dict[str, Any] = {
            "date": kept_dates[day],
            "available_stocks": int(all_valid.sum()),
            "selected_stocks": count,
            "oof_mae_all": float(all_residual.mean()),
            "oof_mae_selected": float(selected_day_residual.mean()),
            "oof_mae_unselected": (
                float(absolute_residuals[day, unselected].mean())
                if unselected.any()
                else np.nan
            ),
            "oof_r2_all": float(r2),
            "target_mean_all": float(all_y.mean()),
            "target_mean_selected": float(padded_y[day, chosen].mean()),
            "target_std_all": float(all_y.std(ddof=0)),
            "target_std_selected": float(padded_y[day, chosen].std(ddof=0)),
        }
        for group in range(NUM_GROUPS):
            record[f"selected_quintile_{group + 1}"] = int(
                np.count_nonzero(padded_labels[day, chosen] == group)
            )
        audit_rows.append(record)

    weights = exponential_weights(day_count)
    weights = (weights / weights.mean()).astype(np.float32)
    panel = DailyRegressionPanel(
        features=selected_x,
        targets=selected_y,
        labels=selected_labels,
        valid=selected_valid,
        date_weights=weights,
        dates=pd.DatetimeIndex(kept_dates),
    )
    return DenoisedPanelResult(
        panel=panel,
        audit=pd.DataFrame.from_records(audit_rows),
        selected_global_positions=selected_global,
        selected_oof_absolute_residuals=selected_residual,
    )

def atomic_npz(path: Path, **arrays: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    os.replace(temporary, path)

def training_date_weights(length: int) -> np.ndarray:
    """Exponential daily weights normalized to mean one; oldest:newest = 1:3."""
    if length <= 0:
        return np.empty(0, dtype=np.float32)
    if length == 1:
        return np.ones(1, dtype=np.float32)
    position = np.linspace(0.0, 1.0, length, dtype=np.float64)
    weights = np.exp(math.log(TRAINING_NEWEST_TO_OLDEST_WEIGHT) * position)
    return (weights / weights.mean()).astype(np.float32)

def _daily_pairwise_loss(
    *,
    differences: torch.Tensor,
    positive: torch.Tensor,
    negative: torch.Tensor,
    date_weights: torch.Tensor,
    temperature: float,
) -> torch.Tensor:
    pair_mask = positive.unsqueeze(2) & negative.unsqueeze(1)
    pair_loss = torch.nn.functional.softplus(-differences / temperature)
    pair_count = pair_mask.sum(dim=(1, 2)).clamp_min(1)
    daily_loss = (pair_loss * pair_mask).sum(dim=(1, 2)) / pair_count
    return (daily_loss * date_weights).sum() / date_weights.sum().clamp_min(1e-12)

def dual_ranking_loss(
    logits: torch.Tensor,
    labels: torch.Tensor,
    valid: torch.Tensor,
    date_weights: torch.Tensor,
    temperature: float,
    top20_bottom80_weight: float,
    top20_bottom20_weight: float,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Time-weighted RankNet losses on daily complete cross sections."""
    probabilities = torch.softmax(logits.float(), dim=-1)
    group_values = torch.arange(
        1, NUM_GROUPS + 1, device=logits.device, dtype=torch.float32
    )
    scores = probabilities @ group_values
    differences = scores.unsqueeze(2) - scores.unsqueeze(1)
    top20 = valid & labels.eq(NUM_GROUPS - 1)
    bottom80 = valid & labels.ge(0) & labels.lt(NUM_GROUPS - 1)
    bottom20 = valid & labels.eq(0)
    top_vs_bottom80 = _daily_pairwise_loss(
        differences=differences,
        positive=top20,
        negative=bottom80,
        date_weights=date_weights,
        temperature=temperature,
    )
    top_vs_bottom20 = _daily_pairwise_loss(
        differences=differences,
        positive=top20,
        negative=bottom20,
        date_weights=date_weights,
        temperature=temperature,
    )
    total = (
        top20_bottom80_weight * top_vs_bottom80
        + top20_bottom20_weight * top_vs_bottom20
    )
    return total, top_vs_bottom80, top_vs_bottom20

def train_one_epoch(
    *,
    model: FiveGroupSoftsignMLP,
    panel: DeviceRegressionPanel,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    amp_dtype: torch.dtype,
    batch_days: int,
    gradient_clip_norm: float,
    temperature: float,
    top20_bottom80_weight: float,
    top20_bottom20_weight: float,
    seed: int,
) -> tuple[float, float, float]:
    model.train()
    order = np.random.default_rng(seed).permutation(len(panel.features))
    metrics: list[tuple[torch.Tensor, torch.Tensor, torch.Tensor]] = []
    for start in range(0, len(order), batch_days):
        rows = torch.as_tensor(order[start : start + batch_days], device=device)
        features = panel.features.index_select(0, rows)
        labels = panel.labels.index_select(0, rows)
        valid = panel.valid.index_select(0, rows)
        weights = panel.date_weights.index_select(0, rows)
        optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast(
            device_type=device.type, dtype=amp_dtype, enabled=True
        ):
            logits = model(features)
        total, top_bottom80, top_bottom20 = dual_ranking_loss(
            logits,
            labels,
            valid,
            weights,
            temperature,
            top20_bottom80_weight,
            top20_bottom20_weight,
        )
        total.backward()
        nn.utils.clip_grad_norm_(model.parameters(), gradient_clip_norm)
        optimizer.step()
        metrics.append(
            (total.detach(), top_bottom80.detach(), top_bottom20.detach())
        )
    stacked = torch.stack([torch.stack(item) for item in metrics])
    means = stacked.mean(dim=0).cpu().numpy()
    return float(means[0]), float(means[1]), float(means[2])

@torch.inference_mode()
def predict_probabilities(
    model: FiveGroupSoftsignMLP,
    features: np.ndarray,
    device: torch.device,
    batch_size: int,
    amp_dtype: torch.dtype,
) -> np.ndarray:
    model.eval()
    output = np.empty((len(features), NUM_GROUPS), dtype=np.float32)
    for start in range(0, len(features), batch_size):
        end = min(start + batch_size, len(features))
        batch = torch.from_numpy(features[start:end]).to(device, non_blocking=True)
        with torch.amp.autocast(
            device_type=device.type, dtype=amp_dtype, enabled=True
        ):
            output[start:end] = torch.softmax(
                model(batch).float(), dim=1
            ).cpu().numpy()
    if not np.isfinite(output).all():
        raise FloatingPointError("v5五分组概率存在NaN或Inf")
    if not np.allclose(output.sum(axis=1), 1.0, atol=2e-4):
        raise FloatingPointError("v5五分组概率和不为1")
    return output

def expected_group_score(probabilities: np.ndarray) -> np.ndarray:
    return np.asarray(probabilities, dtype=np.float32) @ GROUP_VALUES

def _materialize_final_outputs(
    output_root: Path,
    predictions_by_category: dict[str, list[pd.DataFrame]],
    market_index: pd.MultiIndex,
    first_output_month: str,
    final_output_month: str,
) -> None:
    first = pd.Period(first_output_month, freq="M").start_time.normalize()
    final = pd.Period(final_output_month, freq="M").end_time.normalize()
    expected = _window_index(market_index, first, final)
    expected_pairs = pd.MultiIndex.from_arrays(
        [expected.get_level_values("date"), expected.get_level_values("symbol")],
        names=["available_date", "symbol"],
    )
    temporary = output_root / f".final.{uuid.uuid4().hex}.tmp"
    temporary.mkdir(parents=True)
    summary: dict[str, Any] = {
        "version": "v5_denoised_five_group_dual_rank",
        "first_output_month": first_output_month,
        "final_output_month": final_output_month,
        "expected_rows_per_category": len(expected_pairs),
        "probability_contract": "five_group_softmax",
        "factor_value_contract": (
            "sum(prob_group_k * k), k=1..5, higher_is_better"
        ),
        "categories": {},
    }
    try:
        for category_cn, category_en in CATEGORY_NAMES.items():
            frame = pd.concat(
                predictions_by_category[category_cn], ignore_index=True
            ).sort_values(["available_date", "symbol"], kind="mergesort")
            actual_pairs = pd.MultiIndex.from_frame(frame[["available_date", "symbol"]])
            if len(frame) != len(expected_pairs) or len(
                expected_pairs.difference(actual_pairs)
            ):
                raise ValueError(f"{category_cn}最终预测网格不完整")
            factor_dir = temporary / category_en
            wide = frame.pivot(index=["signal_date", "available_date"], columns="symbol", values="factor_value").sort_index().reset_index()
            wide.columns.name = None
            write_output_parquet(wide, factor_dir / "raw.parquet")
            summary["categories"][category_cn] = {
                "directory": category_en,
                "rows": len(frame),
                "dates": int(frame["available_date"].nunique()),
                "symbols": int(frame["symbol"].nunique()),
            }
        atomic_json(summary, temporary / "validation_summary.json")
        final_root = output_root / "final"
        backup = output_root / f".final.previous.{uuid.uuid4().hex}"
        if final_root.exists():
            os.replace(final_root, backup)
        os.replace(temporary, final_root)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise



VERSION = "v5_denoised_enhance_8y_ten_categories_2020_20260630"

DEFAULT_OUTPUT_ROOT = (
    PROJECT_ROOT / "outputs_mlp_v5_denoised_enhance_only_2025_2026"
)

FIRST_OUTPUT_MONTH = "2025-01"

FINAL_OUTPUT_MONTH = "2026-06"

TRAINING_MONTHS = 96

FACTORS_PER_CATEGORY = 50

CATEGORY_INPUT_COUNTS = {category: FACTORS_PER_CATEGORY for category in CATEGORY_NAMES}

IC_FACTORS_PER_CATEGORY = 10


SELECTION_NEWEST_TO_OLDEST_WEIGHT = 2.0

TRAINING_NEWEST_TO_OLDEST_WEIGHT = 3.0

def configure_category_input_counts(factor_to_category: dict[str, str]) -> None:
    """新分类按实际容量限制输入维数，最多50个，不复制因子补足维数。"""
    for category in CATEGORY_NAMES:
        capacity = sum(assigned == category for assigned in factor_to_category.values())
        if capacity < 1:
            raise ValueError(f"类别{category}没有可用配置因子")
        CATEGORY_INPUT_COUNTS[category] = min(FACTORS_PER_CATEGORY, capacity)


def input_count_for_category(category: str) -> int:
    return CATEGORY_INPUT_COUNTS[category]


def ic_count_for_category(category: str) -> int:
    return min(IC_FACTORS_PER_CATEGORY, input_count_for_category(category))


def return_count_for_category(category: str) -> int:
    return input_count_for_category(category) - ic_count_for_category(category)


def build_windows_8y(calendar: pd.DatetimeIndex) -> list[Window]:
    """建立96个月窗口，并为5日标签预留6个交易日成熟期。"""
    first = pd.Period(FIRST_OUTPUT_MONTH, freq="M")
    final = pd.Period(FINAL_OUTPUT_MONTH, freq="M")
    raw: list[dict[str, Any]] = []
    for output_period in pd.period_range(first, final, freq="M"):
        prediction_dates = calendar[
            (calendar >= output_period.start_time.normalize())
            & (calendar <= output_period.end_time.normalize())
        ]
        if prediction_dates.empty:
            raise ValueError(f"{output_period}没有预测交易日")
        prediction_position = int(calendar.get_loc(prediction_dates[0]))
        endpoint_position = prediction_position - 1
        endpoint = pd.Timestamp(calendar[endpoint_position])
        window_start_floor = (output_period - TRAINING_MONTHS).start_time.normalize()
        validation_floor = (output_period - 3).start_time.normalize()
        window_dates = calendar[
            (calendar >= window_start_floor) & (calendar <= endpoint)
        ]
        validation_dates = calendar[
            (calendar >= validation_floor) & (calendar <= endpoint)
        ]
        if window_dates.empty or validation_dates.empty:
            raise ValueError(f"{output_period}无法形成{TRAINING_MONTHS}个月窗口")
        validation_position = int(calendar.get_loc(validation_dates[0]))
        train_end_position = validation_position - FUTURE_PRICE_STEPS - 1
        factor_end_position = endpoint_position - FUTURE_PRICE_STEPS
        if train_end_position < int(calendar.get_loc(window_dates[0])):
            raise ValueError(f"{output_period}的历史训练窗口不足")
        raw.append(
            {
                "output_month": str(output_period),
                "endpoint": endpoint,
                "window_start": pd.Timestamp(window_dates[0]),
                "train_end": pd.Timestamp(calendar[train_end_position]),
                "validation_start": pd.Timestamp(validation_dates[0]),
                "factor_end": pd.Timestamp(calendar[factor_end_position]),
                "prediction_start": pd.Timestamp(prediction_dates[0]),
                "prediction_end": pd.Timestamp(prediction_dates[-1]),
            }
        )
    return [
        Window(number=i + 1, total=len(raw), **item)
        for i, item in enumerate(raw)
    ]

def select_factors_enhanced(
    *,
    window: Window,
    category_names: list[str],
    factor_to_category: dict[str, str],
    ic_store: ICMatrixStore,
    return_store: dict[str, WeeklyReturnSeries],
) -> pd.DataFrame:
    """每类最多50个输入，先选最多10个加权|IC|因子，再选收益因子。"""
    records: list[dict[str, Any]] = []
    for category in category_names:
        category_factors = sorted(
            factor
            for factor, assigned in factor_to_category.items()
            if assigned == category
        )
        ic_candidates: list[dict[str, Any]] = []
        for factor in category_factors:
            weighted_ic = ic_store.weighted_mean(
                factor, window.window_start, window.factor_end
            )
            if not np.isfinite(weighted_ic):
                continue
            ic_candidates.append(
                {
                    "category_cn": category,
                    "factor_name": factor,
                    "selection_stage": "weighted_abs_ic_8y",
                    "weighted_ic": weighted_ic,
                    "weighted_abs_ic": abs(weighted_ic),
                    "weighted_higher_return": np.nan,
                    "weighted_lower_return": np.nan,
                    "selection_metric": abs(weighted_ic),
                    "selection_direction": "higher" if weighted_ic >= 0 else "lower",
                    "input_orientation": 1 if weighted_ic >= 0 else -1,
                }
            )
        ic_candidates.sort(
            key=lambda row: (-row["weighted_abs_ic"], row["factor_name"])
        )
        required_ic_count = ic_count_for_category(category)
        if len(ic_candidates) < required_ic_count:
            raise ValueError(
                f"{window.output_month}/{category}只有{len(ic_candidates)}个可用IC因子"
            )
        selected_ic = ic_candidates[:required_ic_count]
        selected_names = {row["factor_name"] for row in selected_ic}

        return_candidates: list[dict[str, Any]] = []
        for factor in category_factors:
            if factor in selected_names:
                continue
            series = return_store.get(factor)
            if series is None:
                continue
            higher, lower = series.weighted_compounded(
                window.window_start, window.endpoint
            )
            if not np.isfinite(higher) or not np.isfinite(lower):
                continue
            direction = "higher" if higher >= lower else "lower"
            return_candidates.append(
                {
                    "category_cn": category,
                    "factor_name": factor,
                    "selection_stage": "weighted_weekly_return_8y",
                    "weighted_ic": np.nan,
                    "weighted_abs_ic": np.nan,
                    "weighted_higher_return": higher,
                    "weighted_lower_return": lower,
                    "selection_metric": max(higher, lower),
                    "selection_direction": direction,
                    "input_orientation": 1 if direction == "higher" else -1,
                }
            )
        return_candidates.sort(
            key=lambda row: (-row["selection_metric"], row["factor_name"])
        )
        required_return_count = return_count_for_category(category)
        if len(return_candidates) < required_return_count:
            raise ValueError(
                f"{window.output_month}/{category}排除IC入选项后只有"
                f"{len(return_candidates)}个可用收益因子，"
                f"至少需要{required_return_count}个"
            )
        selected_return = return_candidates[:required_return_count]
        chosen = [*selected_ic, *selected_return]
        for selection_rank, row in enumerate(chosen, start=1):
            if row["selection_stage"] == "weighted_abs_ic_8y":
                stage_rank = selection_rank
            else:
                stage_rank = selection_rank - required_ic_count
            records.append(
                {
                    "selection_rank": selection_rank,
                    "stage_rank": stage_rank,
                    **row,
                }
            )

    result = pd.DataFrame.from_records(records)
    for category in category_names:
        subset = result.loc[result["category_cn"].eq(category)]
        expected_count = input_count_for_category(category)
        if (
            len(subset) != expected_count
            or subset["factor_name"].nunique() != expected_count
            or subset["selection_rank"].astype(int).tolist()
            != list(range(1, expected_count + 1))
        ):
            raise ValueError(
                f"{window.output_month}/{category}未形成"
                f"{expected_count}个不重复输入因子"
            )
    return result

class EnhancedFiveGroupSoftsignMLP(nn.Module):
    """动态输入维度、三层Softsign隐藏层、五分组logits输出。"""

    def __init__(self, input_count: int) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        previous = input_count
        for width, dropout in zip(HIDDEN_DIMS, (0.15, 0.10, 0.05), strict=True):
            layers.extend(
                [
                    nn.Linear(previous, width),
                    nn.LayerNorm(width),
                    nn.Softsign(),
                    nn.Dropout(dropout),
                ]
            )
            previous = width
        layers.append(nn.Linear(previous, NUM_GROUPS))
        self.network = nn.Sequential(*layers)
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features)

def oriented_features(
    selected: pd.DataFrame, index: pd.MultiIndex, expected_count: int
) -> np.ndarray:
    """加载任意列数的中性化因子；绕开旧模块固定30列的输入断言。"""
    ordered = selected.sort_values("selection_rank")
    names = ordered["factor_name"].astype(str).tolist()
    orientations = ordered["input_orientation"].to_numpy(dtype=np.float32)
    if len(names) != expected_count:
        raise ValueError(f"增强版该类别必须恰好加载{expected_count}个因子")
    matrix = np.empty((len(index), len(names)), dtype=np.float32)
    for column, factor_name in enumerate(names):
        factor = factors_select._load_cached_factor(factor_name)
        matrix[:, column] = factor.reindex(index).to_numpy(dtype=np.float32)
    dates = index.get_level_values("date").to_numpy(dtype="datetime64[ns]")
    features = _preprocess_features(matrix, dates)
    features *= orientations.reshape(1, -1)
    return np.ascontiguousarray(features, dtype=np.float32)

def initialize_model(
    seed: int, device: torch.device, input_count: int
) -> EnhancedFiveGroupSoftsignMLP:
    with MODEL_INIT_LOCK:
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        return EnhancedFiveGroupSoftsignMLP(input_count).to(device)

def fit_fixed_epochs(
    *,
    category_en: str,
    full_panel: DailyRegressionPanel,
    device: torch.device,
    stream: torch.cuda.Stream,
    seed: int,
    input_count: int,
    epochs: int,
    batch_days: int,
    learning_rate: float,
    min_learning_rate: float,
    weight_decay: float,
    gradient_clip_norm: float,
    temperature: float,
    top20_bottom80_weight: float,
    top20_bottom20_weight: float,
) -> tuple[EnhancedFiveGroupSoftsignMLP, pd.DataFrame, dict[str, Any]]:
    amp_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    model = initialize_model(seed, device, input_count)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=weight_decay
    )
    records: list[dict[str, Any]] = []
    with torch.cuda.stream(stream):
        device_panel = panel_to_device(full_panel, device)
        for epoch in range(1, epochs + 1):
            started = time.monotonic()
            learning_rate_now = scheduled_learning_rate(
                epoch, epochs, learning_rate, min_learning_rate
            )
            for group in optimizer.param_groups:
                group["lr"] = learning_rate_now
            total, top_bottom80, top_bottom20 = train_one_epoch(
                model=model,
                panel=device_panel,
                optimizer=optimizer,
                device=device,
                amp_dtype=amp_dtype,
                batch_days=batch_days,
                gradient_clip_norm=gradient_clip_norm,
                temperature=temperature,
                top20_bottom80_weight=top20_bottom80_weight,
                top20_bottom20_weight=top20_bottom20_weight,
                seed=seed + epoch,
            )
            record = {
                "epoch": epoch,
                "learning_rate": learning_rate_now,
                "train_total_loss": total,
                "train_weighted_top20_bottom80_rank_loss": top_bottom80,
                "train_weighted_top20_bottom20_rank_loss": top_bottom20,
                "elapsed_seconds": time.monotonic() - started,
            }
            records.append(record)
            print(
                f"TRAIN_EPOCH_V5_ENHANCE category={category_en} "
                f"epoch={epoch}/{epochs} total_loss={total:.8f} "
                f"top20_bottom80={top_bottom80:.8f} "
                f"top20_bottom20={top_bottom20:.8f} "
                f"elapsed_seconds={record['elapsed_seconds']:.2f}",
                flush=True,
            )
        stream.synchronize()
    metadata = {
        "training_mode": "single_stage_full_96_month_fixed_epochs",
        "fixed_epochs": epochs,
        "training_months": TRAINING_MONTHS,
        "validation_enabled": False,
        "date_weight_newest_to_oldest": TRAINING_NEWEST_TO_OLDEST_WEIGHT,
        "top20_bottom80_loss_weight": top20_bottom80_weight,
        "top20_bottom20_loss_weight": top20_bottom20_weight,
    }
    return model.eval(), pd.DataFrame(records), metadata

def category_complete(
    path: Path,
    expected_rows: int,
    target_stocks: int,
    expected_input_count: int,
) -> bool:
    required = [
        path / "selected_factors.parquet",
        path / "epochs.parquet",
        path / "best_model.pt",
        path / "predictions.parquet",
        path / "metadata.json",
        path / "denoise_selected_rows.npz",
        path / "denoise_daily_summary.parquet",
        path / "denoise_metadata.json",
    ]
    if not all(item.is_file() for item in required):
        return False
    try:
        predictions = pd.read_parquet(path / "predictions.parquet")
        probability_columns = [
            f"prob_group_{group}" for group in range(1, NUM_GROUPS + 1)
        ]
        values = predictions[["factor_value", *probability_columns]].to_numpy()
        audit = pd.read_parquet(path / "denoise_daily_summary.parquet")
        expected_selected = np.minimum(audit["available_stocks"], target_stocks)
        with np.load(path / "denoise_selected_rows.npz") as archive:
            denoise_days = archive["selected_global_positions"].shape[0]
        metadata = json.loads((path / "metadata.json").read_text(encoding="utf-8"))
        checkpoint = torch.load(
            path / "best_model.pt", map_location="cpu", weights_only=False
        )
        selected = pd.read_parquet(path / "selected_factors.parquet")
        return (
            len(predictions) == expected_rows
            and np.isfinite(values).all()
            and np.allclose(
                predictions[probability_columns].sum(axis=1), 1.0, atol=2e-4
            )
            and predictions["factor_value"].between(1.0, 5.0).all()
            and not audit.empty
            and (audit["selected_stocks"] > 0).all()
            and np.array_equal(
                audit["selected_stocks"].to_numpy(),
                expected_selected.to_numpy(),
            )
            and denoise_days == len(audit)
            and metadata.get("version") == VERSION
            and checkpoint.get("version") == VERSION
            and checkpoint.get("architecture", [None])[0] == expected_input_count
            and len(selected) == expected_input_count
            and selected["factor_name"].nunique() == expected_input_count
        )
    except Exception:
        return False


def materialize_final(
    output_root: Path,
    predictions_by_category: dict[str, list[pd.DataFrame]],
    market_index: pd.MultiIndex,
) -> None:
    _materialize_final_outputs(
        output_root,
        predictions_by_category,
        market_index,
        FIRST_OUTPUT_MONTH,
        FINAL_OUTPUT_MONTH,
    )
    summary_path = output_root / "final" / "validation_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary.update(
        {
            "version": VERSION,
            "training_months": TRAINING_MONTHS,
            "inputs_per_category": {
                category: input_count_for_category(category)
                for category in CATEGORY_NAMES
            },
            "factor_selection": (
                "ten categories: up to 50 configured factors per category; "
                "up to 10 weighted_abs_ic factors, then weighted_return factors"
            ),
        }
    )
    atomic_json(summary, summary_path)


def run_pipeline(args: argparse.Namespace) -> None:
    source_root = args.source_root.resolve()
    ic_root = args.ic_root.resolve()
    return_root = args.return_root.resolve()
    output_root = args.output_root.resolve()
    factors_select._assert_source_is_read_only_scope(source_root, output_root)
    if output_root.exists() and any(output_root.iterdir()) and not args.resume:
        raise FileExistsError(f"输出目录非空：{output_root}；续跑请添加--resume")

    factors_select._SOURCE_ROOT = source_root
    factors_select._IC_VERSION = "neutralization"
    factors_select._FACTOR_VALUE_CACHE.clear()
    configs = factors_select._load_configs(
        args.expansion_factor_config, args.base_factor_config
    )
    factor_names = sorted(configs)
    category_names, factor_to_category = factors_select._load_categories(
        configs, set(factor_names)
    )
    if category_names != list(CATEGORY_NAMES):
        raise ValueError(f"类别顺序必须为{list(CATEGORY_NAMES)}")
    configure_category_input_counts(factor_to_category)

    full_calendar = factors_select._read_trading_calendar(
        legacy.DEFAULT_START_DATE, FINAL_OUTPUT_MONTH
    )
    windows = build_windows_8y(full_calendar)
    print(
        "MLP_V5_ENHANCE_PLAN "
        f"windows={len(windows)} range={FIRST_OUTPUT_MONTH}..{FINAL_OUTPUT_MONTH} "
        "training_months=96 factor_selection=weighted_ic10_return40_8y "
        "selection_date_weight_oldest_newest=1:2 "
        f"inputs_per_category={CATEGORY_INPUT_COUNTS} "
        "denoise=recompute_daily_cross_fitted_additive_piecewise_ridge "
        f"denoise_keep={args.denoise_stocks} folds={args.denoise_folds} "
        f"ridge_alpha={args.denoise_ridge_alpha} spline_knot={args.spline_knot} "
        "quintile_balance=equal model=five_group_softsign "
        f"loss={args.top20_bottom80_loss_weight}*weighted_top20_bottom80+"
        f"{args.top20_bottom20_loss_weight}*weighted_top20_bottom20 "
        "training_date_weight_oldest_newest=1:3 "
        f"epochs={args.epochs} concurrent_mlp={args.mlp_workers} "
        f"output_root={output_root}",
        flush=True,
    )
    for window in windows:
        print(
            f"WINDOW_PLAN {window.number}/{window.total} "
            f"output={window.output_month} "
            f"train={window.window_start:%Y-%m-%d}..{window.factor_end:%Y-%m-%d} "
            "stock_selection=daily_independent_recomputed",
            flush=True,
        )
    if args.plan_only:
        return

    if not torch.cuda.is_available():
        raise RuntimeError("v5增强版多类别并发训练和每日Ridge筛选要求CUDA")
    if args.gpu_id < 0 or args.gpu_id >= torch.cuda.device_count():
        raise ValueError("gpu-id超出可用范围")
    torch.cuda.set_device(args.gpu_id)
    device = torch.device(f"cuda:{args.gpu_id}")
    torch.set_float32_matmul_precision("high")
    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass

    output_root.mkdir(parents=True, exist_ok=True)
    factors_select._validate_source_factor_dirs(source_root, factor_names)
    ic_store, return_store = preload_metric_stores(
        factor_names, ic_root, return_root, args.metric_read_workers
    )
    if (
        ic_store.dates.min() > windows[0].window_start.to_datetime64()
        or ic_store.dates.max() < windows[-1].factor_end.to_datetime64()
    ):
        raise ValueError("预计算IC日期不足以覆盖增强版八年窗口")

    market_start = windows[0].window_start.strftime("%Y-%m-%d")
    market_end = windows[-1].prediction_end.strftime("%Y-%m-%d")
    loader = FactorDataLoader(runtime_inputs=legacy.runtime_inputs('zz500'),
                              universe='zz500',context_only=True,
                              start=market_start,end=market_end)
    market_data = loader.load_all().sort_index()
    market_index = market_data.index
    legacy._PIPELINE_DATES = pd.DatetimeIndex(
        market_index.get_level_values("date").unique()
    ).sort_values()
    forward_returns = calc_forward_returns(
        market_data, period=FORWARD_PERIOD, price_col="close_hfq"
    )
    predictions_by_category: dict[str, list[pd.DataFrame]] = {
        category: [] for category in category_names
    }

    for window in windows:
        window_root = output_root / "windows" / f"after_{window.endpoint:%Y_%m_%d}"
        prediction_index, prediction_metadata = _make_prediction_grid(
            market_index,
            full_calendar,
            window.prediction_start,
            window.prediction_end,
        )
        expected_prediction_rows = len(prediction_metadata)
        completed = [
            category
            for category in category_names
            if args.resume
            and category_complete(
                window_root / CATEGORY_NAMES[category],
                expected_prediction_rows,
                args.denoise_stocks,
                input_count_for_category(category),
            )
        ]
        for category in completed:
            predictions_by_category[category].append(
                pd.read_parquet(
                    window_root
                    / CATEGORY_NAMES[category]
                    / "predictions.parquet"
                )
            )
            print(
                f"CATEGORY_RESUME_SKIP_V5_ENHANCE output={window.output_month} "
                f"category={category}",
                flush=True,
            )
        pending = [category for category in category_names if category not in completed]
        if not pending:
            continue

        selected_path = window_root / "selected_factors.parquet"
        if args.resume and selected_path.is_file():
            selected = pd.read_parquet(selected_path)
        else:
            selected = select_factors_enhanced(
                window=window,
                category_names=category_names,
                factor_to_category=factor_to_category,
                ic_store=ic_store,
                return_store=return_store,
            )
            atomic_parquet(selected, selected_path)
        expected_total = sum(input_count_for_category(c) for c in category_names)
        if len(selected) != expected_total:
            raise ValueError(
                f"{window.output_month}输入因子总数不是{expected_total}"
            )
        atomic_json(
            {
                **asdict(window),
                "version": VERSION,
                "training_months": TRAINING_MONTHS,
                "factor_selection": (
                    "8y weighted abs IC up to10 then, excluding duplicates, "
                    "weighted weekly return to min(50, configured_category_capacity)"
                ),
                "inputs_per_category": {
                    category: input_count_for_category(category)
                    for category in category_names
                },
                "selection_date_weight_newest_to_oldest": (
                    SELECTION_NEWEST_TO_OLDEST_WEIGHT
                ),
                "stock_selection": "independent per date and category, recomputed",
                "stock_selection_label_end": window.factor_end,
                "prediction_month_filtered": False,
                "denoise_stocks": args.denoise_stocks,
                "denoise_folds": args.denoise_folds,
                "ridge_alpha": args.denoise_ridge_alpha,
                "spline_knot": args.spline_knot,
                "output": "five_group_softmax_and_expected_group_score",
                "loss": "weighted_top20_bottom80_plus_weighted_top20_bottom20",
                "loss_weights": [
                    args.top20_bottom80_loss_weight,
                    args.top20_bottom20_loss_weight,
                ],
            },
            window_root / "window.json",
        )
        full_index = _window_index(
            market_index, window.window_start, window.factor_end
        )
        full_returns = forward_returns.reindex(full_index)

        def train_category(category: str) -> tuple[str, pd.DataFrame, dict[str, Any]]:
            category_en = CATEGORY_NAMES[category]
            category_root = window_root / category_en
            category_selected = selected.loc[
                selected["category_cn"].eq(category)
            ].sort_values("selection_rank")
            input_count = input_count_for_category(category)
            if len(category_selected) != input_count:
                raise ValueError(
                    f"{window.output_month}/{category}输入因子不是{input_count}个"
                )
            atomic_parquet(category_selected, category_root / "selected_factors.parquet")
            started = time.monotonic()
            full_features = oriented_features(
                category_selected, full_index, input_count
            )
            prediction_features = oriented_features(
                category_selected, prediction_index, input_count
            )
            if full_features.shape[1] != input_count:
                raise ValueError("增强版特征矩阵列数与类别约定不一致")
            stream = torch.cuda.Stream(device=device)
            denoised = build_denoised_daily_panel(
                features=full_features,
                returns=full_returns,
                index=full_index,
                device=device,
                stream=stream,
                target_stocks=args.denoise_stocks,
                fold_count=args.denoise_folds,
                ridge_alpha=args.denoise_ridge_alpha,
                day_batch=args.denoise_day_batch,
                spline_knot=args.spline_knot,
            )
            denoised.panel.date_weights = training_date_weights(
                len(denoised.panel.dates)
            )
            atomic_parquet(denoised.audit, category_root / "denoise_daily_summary.parquet")
            atomic_npz(
                category_root / "denoise_selected_rows.npz",
                selected_global_positions=denoised.selected_global_positions,
                selected_oof_absolute_residuals=(
                    denoised.selected_oof_absolute_residuals
                ),
                dates_ns=denoised.panel.dates.to_numpy(dtype="datetime64[ns]").astype(
                    np.int64
                ),
            )
            denoise_metadata = {
                "method": "daily_cross_fitted_additive_piecewise_linear_ridge",
                "selection_artifact_reused": False,
                "selection_recomputed_by_enhanced_v5": True,
                "selection_scope": "independent_for_each_date_category_and_monthly_window",
                "features_per_category": input_count,
                "features_preprocessed_on_full_daily_cross_section_before_filtering": True,
                "fold_assignment": "stable_blake2b_symbol_hash",
                "folds": args.denoise_folds,
                "ridge_alpha": args.denoise_ridge_alpha,
                "basis": "per_factor_[x,relu(x-knot),relu(-x-knot)]",
                "spline_knot": args.spline_knot,
                "score": "absolute_out_of_fold_residual",
                "target_stocks_per_day": args.denoise_stocks,
                "quintile_constraint": (
                    "equal realised-return-quintile quota; 40 each when target=200"
                ),
                "target": "matured clipped forward_5d_return_percentage_points",
                "prediction_month_filtering": False,
                "days": len(denoised.panel.dates),
                "mean_available_stocks": float(
                    denoised.audit["available_stocks"].mean()
                ),
                "mean_selected_stocks": float(
                    denoised.audit["selected_stocks"].mean()
                ),
            }
            atomic_json(denoise_metadata, category_root / "denoise_metadata.json")
            category_position = category_names.index(category)
            seed = args.seed + window.number * 100 + category_position
            model, epoch_metrics, training_metadata = fit_fixed_epochs(
                category_en=category_en,
                full_panel=denoised.panel,
                device=device,
                stream=stream,
                seed=seed,
                input_count=input_count,
                epochs=args.epochs,
                batch_days=args.daily_batch_days,
                learning_rate=args.learning_rate,
                min_learning_rate=args.min_learning_rate,
                weight_decay=args.weight_decay,
                gradient_clip_norm=args.gradient_clip_norm,
                temperature=args.ranking_temperature,
                top20_bottom80_weight=args.top20_bottom80_loss_weight,
                top20_bottom20_weight=args.top20_bottom20_loss_weight,
            )
            atomic_parquet(epoch_metrics, category_root / "epochs.parquet")
            atomic_model(
                {
                    "version": VERSION,
                    "architecture": [
                        input_count,
                        *HIDDEN_DIMS,
                        NUM_GROUPS,
                    ],
                    "hidden_activation": "Softsign",
                    "output": "five_group_logits_and_softmax_probabilities",
                    "factor_value": "sum(prob_group_k * k), k=1..5",
                    "loss": (
                        "weighted_top20_bottom80_ranknet_plus_"
                        "weighted_top20_bottom20_ranknet"
                    ),
                    "denoising": denoise_metadata,
                    "selected_factors": category_selected.to_dict("records"),
                    "window": asdict(window),
                    **training_metadata,
                    "state_dict": clone_state(model),
                },
                category_root / "best_model.pt",
            )
            amp_dtype = (
                torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            )
            with torch.cuda.stream(stream):
                probabilities = predict_probabilities(
                    model,
                    prediction_features,
                    device,
                    args.inference_batch_size,
                    amp_dtype,
                )
                stream.synchronize()
            predictions = prediction_metadata.copy()
            for group in range(1, NUM_GROUPS + 1):
                predictions[f"prob_group_{group}"] = probabilities[:, group - 1]
            predictions["factor_value"] = expected_group_score(probabilities)
            atomic_parquet(predictions, category_root / "predictions.parquet")
            atomic_json(
                {
                    "status": "completed",
                    "version": VERSION,
                    "category_cn": category,
                    "category_en": category_en,
                    "fixed_epochs": args.epochs,
                    "training_months": TRAINING_MONTHS,
                    "inputs_per_category": input_count,
                    "elapsed_seconds": time.monotonic() - started,
                    "validation_enabled": False,
                    "daily_stock_selection": True,
                    "daily_stock_selection_recomputed": True,
                    "dataloader_modified": False,
                },
                category_root / "metadata.json",
            )
            return category, predictions, training_metadata

        training_started = time.monotonic()
        with ThreadPoolExecutor(
            max_workers=min(args.mlp_workers, len(pending)),
            thread_name_prefix="a100-concurrent-mlp-v5-enhance",
        ) as executor:
            futures = {
                executor.submit(train_category, category): category
                for category in pending
            }
            for future in as_completed(futures):
                category, predictions, training_metadata = future.result()
                predictions_by_category[category].append(predictions)
                print(
                    f"CATEGORY_DONE_V5_ENHANCE output={window.output_month} "
                    f"category={category} "
                    f"fixed_epochs={training_metadata['fixed_epochs']}",
                    flush=True,
                )
        torch.cuda.synchronize(device)
        torch.cuda.empty_cache()
        print(
            f"WINDOW_DONE_V5_ENHANCE output={window.output_month} "
            f"categories={len(pending)} "
            f"elapsed_seconds={time.monotonic() - training_started:.2f}",
            flush=True,
        )

    materialize_final(output_root, predictions_by_category, market_index)
    atomic_json(
        {
            "status": "completed",
            "version": VERSION,
            "first_output_month": FIRST_OUTPUT_MONTH,
            "final_output_month": FINAL_OUTPUT_MONTH,
            "training_months": TRAINING_MONTHS,
            "factor_selection": {
                "inputs_per_category": {
                    category: input_count_for_category(category)
                    for category in category_names
                },
                "weighted_abs_ic_count": {
                    category: ic_count_for_category(category) for category in category_names
                },
                "weighted_weekly_return_count": {
                    category: return_count_for_category(category)
                    for category in category_names
                },
                "category_capacity_policy": "min(50, configured_category_capacity)",
                "ic_label_maturity_cutoff": True,
                "ic_and_return_precomputed": True,
                "duplicate_policy": "IC factors excluded before return selection",
                "date_weight_newest_to_oldest": (
                    SELECTION_NEWEST_TO_OLDEST_WEIGHT
                ),
            },
            "stock_selection": {
                "scope": "independent per training date, category, and monthly window",
                "method": "5-fold OOF additive piecewise-linear Ridge residual",
                "recomputed_by_enhanced_v5": True,
                "reused_from_v4": False,
                "keep_per_day": args.denoise_stocks,
                "realised_return_quintile_balanced": True,
                "prediction_month_filtered": False,
            },
            "training": "full 96 months, time weighted 1:3, fixed 6 epochs",
            "hidden_activation": "Softsign",
            "model_output": "five softmax probabilities and expected group score",
            "loss": {
                "top20_bottom80_ranknet_weight": args.top20_bottom80_loss_weight,
                "top20_bottom20_ranknet_weight": args.top20_bottom20_loss_weight,
                "date_weight_newest_to_oldest": TRAINING_NEWEST_TO_OLDEST_WEIGHT,
            },
            "epochs": args.epochs,
            "mlp_workers": args.mlp_workers,
            "source_root": str(source_root),
            "ic_root": str(ic_root),
            "return_root": str(return_root),
            "output_root": str(output_root),
            "training_code": str(Path(__file__).resolve()),
            "historical_training_modules_inlined": True,
            "dataloader_modified_by_this_script": False,
        },
        output_root / "run_manifest.json",
    )
    print(f"MLP_V5_ENHANCE_DONE output={output_root / 'final'}", flush=True)

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expansion-factor-config",
        type=resolve_project_path,
        default=legacy.DEFAULT_EXPANSION_FACTOR_CONFIG,
    )
    parser.add_argument(
        "--base-factor-config",
        type=resolve_project_path,
        default=legacy.DEFAULT_BASE_FACTOR_CONFIG,
    )
    parser.add_argument("--source-root", type=resolve_project_path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--ic-root", type=resolve_project_path, default=DEFAULT_IC_ROOT)
    parser.add_argument("--return-root", type=resolve_project_path, default=DEFAULT_RETURN_ROOT)
    parser.add_argument("--output-root", type=resolve_project_path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--epochs", type=int, default=FIXED_EPOCHS)
    parser.add_argument("--mlp-workers", type=int, default=len(CATEGORY_NAMES))
    parser.add_argument("--metric-read-workers", type=int, default=32)
    parser.add_argument("--daily-batch-days", type=int, default=8)
    parser.add_argument("--inference-batch-size", type=int, default=65536)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--min-learning-rate", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--gradient-clip-norm", type=float, default=5.0)
    parser.add_argument("--ranking-temperature", type=float, default=1.0)
    parser.add_argument(
        "--top20-bottom80-loss-weight",
        type=float,
        default=DEFAULT_TOP20_BOTTOM80_WEIGHT,
    )
    parser.add_argument(
        "--top20-bottom20-loss-weight",
        type=float,
        default=DEFAULT_TOP20_BOTTOM20_WEIGHT,
    )
    parser.add_argument("--denoise-stocks", type=int, default=DEFAULT_DENOISE_STOCKS)
    parser.add_argument("--denoise-folds", type=int, default=DEFAULT_DENOISE_FOLDS)
    parser.add_argument(
        "--denoise-ridge-alpha",
        type=float,
        default=DEFAULT_DENOISE_RIDGE_ALPHA,
    )
    parser.add_argument(
        "--denoise-day-batch", type=int, default=DEFAULT_DENOISE_DAY_BATCH
    )
    parser.add_argument("--spline-knot", type=float, default=DEFAULT_SPLINE_KNOT)
    parser.add_argument("--seed", type=int, default=202609)
    parser.add_argument("--gpu-id", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args(argv)
    if args.epochs != FIXED_EPOCHS:
        parser.error(f"v5增强版固定训练{FIXED_EPOCHS}个epoch，不接受其他值")
    if not 1 <= args.mlp_workers <= len(CATEGORY_NAMES):
        parser.error(f"mlp-workers必须位于1到{len(CATEGORY_NAMES)}")
    if args.metric_read_workers <= 0:
        parser.error("metric-read-workers必须为正数")
    if args.daily_batch_days <= 0 or args.inference_batch_size <= 0:
        parser.error("训练/推理batch参数必须为正数")
    if args.denoise_day_batch <= 0:
        parser.error("denoise-day-batch必须为正数")
    if args.denoise_stocks < NUM_GROUPS:
        parser.error("denoise-stocks不能小于5")
    if not 2 <= args.denoise_folds <= 10:
        parser.error("denoise-folds必须位于2到10")
    if args.denoise_ridge_alpha <= 0 or args.spline_knot <= 0:
        parser.error("Ridge惩罚和样条结点必须为正数")
    if args.ranking_temperature <= 0:
        parser.error("ranking-temperature必须为正数")
    weights = [
        args.top20_bottom80_loss_weight,
        args.top20_bottom20_loss_weight,
    ]
    if any(weight < 0 for weight in weights):
        parser.error("两项损失权重不能为负数")
    if sum(weights) <= 0:
        parser.error("两项损失权重不能同时为0")
    return args

if __name__ == "__main__":
    run_pipeline(parse_args())
