"""alpha158_vsumn_60d：流动性；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'vol': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "vol"),
}


def format_result(result: pd.DataFrame) -> pd.DataFrame:
    result.index.name = 'date'
    result.columns.name = 'symbol'
    return result


def to_wide(data: pd.DataFrame, column: str) -> pd.DataFrame:
    return data[column].unstack('symbol').astype('float32').sort_index()


def calculate_volume_factor(data: pd.DataFrame, window: int) -> pd.DataFrame:
    vol = to_wide(data, 'vol')
    volume_change = vol - vol.shift(1)
    increase = volume_change.clip(lower=0).rolling(window, min_periods=1).sum()
    decrease = (-volume_change).clip(lower=0).rolling(window, min_periods=1).sum()
    denominator = volume_change.abs().rolling(window, min_periods=1).sum() + 1e-12
    return decrease / denominator


@register_factor
@fixed_factor('alpha158_vsumn_60d', {'operation': 'VSUMN', 'window': 60})
class Factor_alpha158_vsumn_60d(BaseFactor):
    """alpha158_vsumn_60d，固定窗口的独立基础因子。"""
    name = 'alpha158_vsumn_60d'
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
        result = calculate_volume_factor(data, window)
        return format_result(result)
