"""volume_60d：流动性；输入来源由本文件维护。"""
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
@fixed_factor('volume_60d', {})
class Factor_volume_60d(BaseFactor):
    INPUTS = INPUTS
    name = 'volume_60d'
    description = "最近60个交易日成交量均值"

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        vol = data['vol'].unstack("symbol").astype(float).sort_index()
        return vol.rolling(60, min_periods=20).mean()
