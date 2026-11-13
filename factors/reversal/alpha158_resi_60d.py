"""alpha158_resi_60d：反转；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

import numpy as np
import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
}


def format_result(result: pd.DataFrame) -> pd.DataFrame:
    result.index.name = 'date'
    result.columns.name = 'symbol'
    return result


def to_wide(data: pd.DataFrame, column: str) -> pd.DataFrame:
    return data[column].unstack('symbol').astype('float32').sort_index()


def rolling_regression(values: pd.DataFrame, window: int) -> pd.DataFrame:

    def calculate(sample: np.ndarray) -> float:
        positions = np.arange(1, len(sample) + 1, dtype=float)
        valid = ~np.isnan(sample)
        x = positions[valid]
        y = sample[valid]
        if len(y) < 2:
            return np.nan
        x_centered = x - x.mean()
        y_centered = y - y.mean()
        x_square_sum = np.sum(x_centered * x_centered)
        if x_square_sum == 0:
            return np.nan
        slope = np.sum(x_centered * y_centered) / x_square_sum
        if np.isnan(sample[-1]):
            return np.nan
        intercept = y.mean() - slope * x.mean()
        return sample[-1] - (slope * positions[-1] + intercept)
    return values.rolling(window, min_periods=1).apply(calculate, raw=True)


def calculate_regression_factor(data: pd.DataFrame, window: int) -> pd.DataFrame:
    close = to_wide(data, 'close_hfq')
    return rolling_regression(close, window) / close


@register_factor
@fixed_factor('alpha158_resi_60d', {'operation': 'RESI', 'window': 60})
class Factor_alpha158_resi_60d(BaseFactor):
    """alpha158_resi_60d，固定窗口的独立基础因子。"""
    name = 'alpha158_resi_60d'
    description = 'Alpha158价格类因子'
    INPUTS = INPUTS

    def __init__(self, operation: str, window: int | None=None, exclude_recent: int | None=None) -> None:
        self.operation = operation.upper()
        if not isinstance(window, int) or window <= 0:
            raise ValueError(f'{self.operation}必须提供正整数window')
        self.window = window
        self.exclude_recent = exclude_recent
        if exclude_recent is not None:
            raise ValueError(f'{self.operation}不支持剔近期窗口')
        else:
            self.factor_name = self.name

    def generate_signals(self, data: pd.DataFrame, constituents: dict[str, set[str]] | None=None) -> pd.DataFrame:
        window = self.window
        result = calculate_regression_factor(data, window)
        return format_result(result)
