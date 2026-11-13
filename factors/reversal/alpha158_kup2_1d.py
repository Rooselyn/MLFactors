"""alpha158_kup2_1d：反转；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

import numpy as np
import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'open_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "open_hfq"),
    'high_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "high_hfq"),
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "low_hfq"),
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
}


def format_result(result: pd.DataFrame) -> pd.DataFrame:
    result.index.name = 'date'
    result.columns.name = 'symbol'
    return result


def to_wide(data: pd.DataFrame, column: str) -> pd.DataFrame:
    return data[column].unstack('symbol').astype('float32').sort_index()


def calculate_candle_factor(data: pd.DataFrame) -> pd.DataFrame:
    open_price = to_wide(data, 'open_hfq')
    high = to_wide(data, 'high_hfq')
    low = to_wide(data, 'low_hfq')
    close = to_wide(data, 'close_hfq')
    spread = high - low + 1e-12
    return (high - np.maximum(open_price, close)) / spread


@register_factor
@fixed_factor('alpha158_kup2_1d', {'operation': 'KUP2'})
class Factor_alpha158_kup2_1d(BaseFactor):
    """alpha158_kup2_1d，固定窗口的独立基础因子。"""
    name = 'alpha158_kup2_1d'
    description = 'Alpha158价格类因子'
    INPUTS = INPUTS

    def __init__(self, operation: str, window: int | None=None, exclude_recent: int | None=None) -> None:
        self.operation = operation.upper()
        self.window = 1
        self.exclude_recent = exclude_recent
        if exclude_recent is not None:
            raise ValueError(f'{self.operation}不支持剔近期窗口')
        else:
            self.factor_name = self.name

    def generate_signals(self, data: pd.DataFrame, constituents: dict[str, set[str]] | None=None) -> pd.DataFrame:
        window = self.window
        result = calculate_candle_factor(data)
        return format_result(result)
