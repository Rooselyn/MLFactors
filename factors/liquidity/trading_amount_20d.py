"""trading_amount_20d：流动性；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
    'vol': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "vol"),
}


@register_factor
@fixed_factor('trading_amount_20d', {})
class Factor_trading_amount_20d(BaseFactor):
    INPUTS = INPUTS
    name = 'trading_amount_20d'
    description = "20日成交金额均值"

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        close_hfq = data['close_hfq'].unstack("symbol").astype(float).sort_index()
        vol = data['vol'].unstack("symbol").astype(float).sort_index()
        amount = close_hfq * vol
        return amount.rolling(20, min_periods=5).mean()
