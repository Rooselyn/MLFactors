"""reversal_60d：反转；输入来源由本文件维护。"""
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


@register_factor
@fixed_factor('reversal_60d', {})
class Factor_reversal_60d(BaseFactor):
    INPUTS = INPUTS
    name = 'reversal_60d'
    description = "过去60个交易日股价反转"

    def generate_signals(self, data: pd.DataFrame, constituents: dict[str, set[str]] | None = None) -> pd.DataFrame:
        close = data['close_hfq'].unstack("symbol").astype(float).sort_index()
        # 过去60日涨幅取负
        return -close.pct_change(60, fill_method=None)
