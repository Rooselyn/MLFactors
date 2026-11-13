"""alpha158_klen_1d：风险；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'open_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "open_hfq"),
    'high_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "high_hfq"),
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "low_hfq"),
}


def format_result(result: pd.DataFrame) -> pd.DataFrame:
    result.index.name = 'date'
    result.columns.name = 'symbol'
    return result


def to_wide(data: pd.DataFrame, column: str) -> pd.DataFrame:
    return data[column].unstack('symbol').astype('float32').sort_index()


def calculate_range_factor(data: pd.DataFrame) -> pd.DataFrame:
    open_price = to_wide(data, 'open_hfq')
    high = to_wide(data, 'high_hfq')
    low = to_wide(data, 'low_hfq')
    return (high - low) / open_price


@register_factor
@fixed_factor('alpha158_klen_1d', {'operation': 'KLEN'})
class Factor_alpha158_klen_1d(BaseFactor):
    """alpha158_klen_1d，固定窗口的独立基础因子。"""
    name = 'alpha158_klen_1d'
    description = 'Alpha158风险类因子'
    INPUTS = INPUTS

    def __init__(self, operation: str, window: int | None=None) -> None:
        self.operation = operation.upper()
        self.window = 1
        self.factor_name = self.name

    def generate_signals(self, data: pd.DataFrame, constituents: dict[str, set[str]] | None=None) -> pd.DataFrame:
        window = self.window
        result = calculate_range_factor(data)
        return format_result(result)
