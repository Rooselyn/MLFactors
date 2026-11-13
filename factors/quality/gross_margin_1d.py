"""gross_margin_1d：质量；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
    'revenue': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "revenue", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'gross_profit': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "revenue", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),), expression='revenue - oper_cost'),
    'industry_sw_1': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "industry_sw_1"),
}


@register_factor
@fixed_factor('gross_margin_1d', {})
class Factor_gross_margin_1d(BaseFactor):
    """Gross margin 1D factor."""
    INPUTS = INPUTS

    name = 'gross_margin_1d'
    description = "Gross margin 1D factor."

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        factor = data["gross_profit"] / data["revenue"].replace(0, pd.NA)

        result = factor.unstack(level="symbol")
        result.index.name = "date"
        result.columns.name = "symbol"
        return result
