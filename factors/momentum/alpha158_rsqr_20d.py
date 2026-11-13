"""alpha158_rsqr_20d：动量；输入来源由本文件维护。"""
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
        y_square_sum = np.sum(y_centered * y_centered)
        if y_square_sum == 0:
            return np.nan
        covariance = np.sum(x_centered * y_centered)
        return covariance ** 2 / (x_square_sum * y_square_sum)
    return values.rolling(window, min_periods=1).apply(calculate, raw=True)


def calculate_regression_factor(data: pd.DataFrame, window: int) -> pd.DataFrame:
    close = to_wide(data, 'close_hfq')
    result = rolling_regression(close, window)
    rolling_std = close.rolling(window, min_periods=1).std()
    return result.mask(np.isclose(rolling_std, 0, atol=2e-05))


@register_factor
@fixed_factor('alpha158_rsqr_20d', {'operation': 'RSQR', 'window': 20})
class Factor_alpha158_rsqr_20d(BaseFactor):
    """alpha158_rsqr_20d，固定窗口的独立基础因子。"""
    name = 'alpha158_rsqr_20d'
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
