"""hml_r_std_84d：风险；输入来源由本文件维护。"""
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
    'high_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "high_hfq"),
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "low_hfq"),
    'vol': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "vol"),
}


@register_factor
@fixed_factor('hml_r_std_84d', {'lookback': 84, 'min_periods': None})
class Factor_hml_r_std_84d(BaseFactor):
    """日内最高涨幅波动率减最低跌幅波动率。"""
    component = 'hml'
    expected_lookback = 84
    INPUTS = INPUTS
    name = 'hml_r_std_84d'
    description = '84 日日内高低收益率波动率之差'

    def __init__(self, lookback: int=84, min_periods: int | None=None) -> None:
        if self.expected_lookback is not None and lookback != self.expected_lookback:
            raise ValueError(f'{self.name} 的 lookback 必须为 {self.expected_lookback}')
        if min_periods is None:
            min_periods = int(np.ceil(lookback * 0.8))
        if lookback <= 0 or min_periods <= 0 or min_periods > lookback:
            raise ValueError('min_periods 必须在 1 到 lookback 之间')
        self.lookback = lookback
        self.min_periods = min_periods

    def generate_signals(self, data: pd.DataFrame, constituents: dict[str, set[str]] | None=None) -> pd.DataFrame:
        required = {'close_hfq', 'high_hfq', 'low_hfq', 'vol'}
        missing = required.difference(data.columns)
        if missing:
            raise KeyError(f'{self.name} 缺少字段: {sorted(missing)}')
        close = data['close_hfq'].unstack('symbol').astype(float).sort_index()
        high = data['high_hfq'].unstack('symbol').reindex_like(close).astype(float)
        low = data['low_hfq'].unstack('symbol').reindex_like(close).astype(float)
        vol = data['vol'].unstack('symbol').reindex_like(close).astype(float)
        valid_close = (close > 0) & (vol > 0)
        previous_close = close.where(valid_close).shift(1)
        high_return = high.where(valid_close & (high > 0)).div(previous_close).sub(1)
        low_return = low.where(valid_close & (low > 0)).div(previous_close).sub(1)
        high_std = high_return.rolling(self.lookback, min_periods=self.min_periods).std()
        low_std = low_return.rolling(self.lookback, min_periods=self.min_periods).std()
        result = high_std - low_std
        result.index.name = 'date'
        result.columns.name = 'symbol'
        return result
