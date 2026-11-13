"""r_std_84d：风险；输入来源由本文件维护。"""
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
    'vol': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "vol"),
}


@register_factor
@fixed_factor('r_std_84d', {'lookback': 84, 'min_periods': None})
class Factor_r_std_84d(BaseFactor):
    """过去 84 个交易日的个股收益率标准差。"""
    INPUTS = INPUTS

    name = 'r_std_84d'
    description = "84 日收益率波动率"

    def __init__(self, lookback: int = 84, min_periods: int | None = None) -> None:
        if lookback != 84:
            raise ValueError("r_std_84d 的 lookback 必须为 84")
        if min_periods is None:
            min_periods = int(np.ceil(lookback * 0.8))
        if lookback <= 0 or min_periods <= 0 or min_periods > lookback:
            raise ValueError("min_periods 必须在 1 到 lookback 之间")

        self.lookback = lookback
        self.min_periods = min_periods

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        required = {'close_hfq', 'vol'}
        missing = required.difference(data.columns)
        if missing:
            raise KeyError(f"r_std_84d 缺少字段: {sorted(missing)}")

        close = data['close_hfq'].unstack("symbol").astype(float).sort_index()
        vol = data['vol'].unstack("symbol").reindex_like(close).astype(float)
        close = close.where((close > 0) & (vol > 0))
        returns = close.pct_change(fill_method=None)
        result = returns.rolling(
            self.lookback,
            min_periods=self.min_periods,
        ).std()
        result.index.name = "date"
        result.columns.name = "symbol"
        return result
