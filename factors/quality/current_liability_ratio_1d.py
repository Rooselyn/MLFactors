"""current_liability_ratio_1d：质量；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
    'total_liab': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "total_liab", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_cur_liab': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "total_cur_liab", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'industry_sw_1': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "industry_sw_1"),
}


@register_factor
@fixed_factor('current_liability_ratio_1d', {})
class Factor_current_liability_ratio_1d(BaseFactor):
    """Current liability ratio 1D factor."""
    INPUTS = INPUTS

    name = 'current_liability_ratio_1d'
    description = "Current liability ratio 1D factor."

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        factor = data['total_cur_liab'] / data['total_liab'].replace(0, pd.NA)

        result = factor.unstack(level="symbol")
        result.index.name = "date"
        result.columns.name = "symbol"
        return result
