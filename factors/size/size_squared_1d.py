"""size_squared_1d：规模；输入来源由本文件维护。"""
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
    'total_mv': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "total_mv"),
}


@register_factor
@fixed_factor('size_squared_1d', {})
class Factor_size_squared_1d(BaseFactor):
    INPUTS = INPUTS
    name = 'size_squared_1d'
    description = "市值平方因子 (ln(MarketCap)^2)"

    def generate_signals(self, data: pd.DataFrame, constituents: dict[str, set[str]] | None = None) -> pd.DataFrame:
        total_mv = data['total_mv'].unstack("symbol").astype(float)
        # 取对数的平方
        return np.log(total_mv.replace(0, np.nan)) ** 2
