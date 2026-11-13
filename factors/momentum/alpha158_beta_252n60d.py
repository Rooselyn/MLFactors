"""alpha158_beta_252n60d：动量；输入来源由本文件维护。"""
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
        return slope
    return values.rolling(window, min_periods=1).apply(calculate, raw=True)


def calculate_net_window_factor(data: pd.DataFrame, lookback: int, exclude_recent: int) -> pd.DataFrame:
    """计算 ``t-lookback`` 至 ``t-exclude_recent`` 的剔近期动量因子。

    价格水平类统计包含区间两端，共 ``lookback-exclude_recent+1`` 个
    交易日观测；涨跌日和价格变化类统计使用连接两端的
    ``lookback-exclude_recent`` 个单日变化。该口径用于隔离中长期动量，
    避免最近若干交易日的短期反转污染信号。
    """
    close = to_wide(data, 'close_hfq')
    lagged_close = close.shift(exclude_recent)
    price_window = lookback - exclude_recent + 1
    change_window = lookback - exclude_recent
    return rolling_regression(lagged_close, price_window) / lagged_close


@register_factor
@fixed_factor('alpha158_beta_252n60d', {'operation': 'BETA', 'window': 252, 'exclude_recent': 60})
class Factor_alpha158_beta_252n60d(BaseFactor):
    """alpha158_beta_252n60d，固定窗口的独立基础因子。"""
    name = 'alpha158_beta_252n60d'
    description = 'Alpha158价格类因子'
    INPUTS = INPUTS

    def __init__(self, operation: str, window: int | None=None, exclude_recent: int | None=None) -> None:
        self.operation = operation.upper()
        if not isinstance(window, int) or window <= 0:
            raise ValueError(f'{self.operation}必须提供正整数window')
        self.window = window
        self.exclude_recent = exclude_recent
        if exclude_recent is not None:
            if not isinstance(exclude_recent, int) or not 0 < exclude_recent < self.window:
                raise ValueError('exclude_recent必须是小于window的正整数')
            self.factor_name = self.name
        else:
            self.factor_name = self.name

    def generate_signals(self, data: pd.DataFrame, constituents: dict[str, set[str]] | None=None) -> pd.DataFrame:
        window = self.window
        result = calculate_net_window_factor(data, lookback=window, exclude_recent=self.exclude_recent)
        return format_result(result)
