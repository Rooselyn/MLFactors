"""alpha158_cntn_60d：反转；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

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


def calculate_count_factor(data: pd.DataFrame, window: int) -> pd.DataFrame:
    """计算过去窗口内上涨、下跌交易日占比及二者之差。"""
    close = to_wide(data, 'close_hfq')
    previous = close.shift(1)
    valid = close.notna() & previous.notna()
    up = close.gt(previous).where(valid).astype(float)
    down = close.lt(previous).where(valid).astype(float)
    up_ratio = up.rolling(window, min_periods=1).mean()
    down_ratio = down.rolling(window, min_periods=1).mean()
    return down_ratio


@register_factor
@fixed_factor('alpha158_cntn_60d', {'operation': 'CNTN', 'window': 60})
class Factor_alpha158_cntn_60d(BaseFactor):
    """alpha158_cntn_60d，固定窗口的独立基础因子。"""
    name = 'alpha158_cntn_60d'
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
        result = calculate_count_factor(data, window)
        return format_result(result)
