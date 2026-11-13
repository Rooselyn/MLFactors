"""net_income_cash_ratio_1d：质量；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
    'n_income': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "n_income", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'n_cashflow_act': ParquetInput("MLFactors/data/zz500/financial_cash_flow/*/*.parquet", "n_cashflow_act", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'industry_sw_1': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "industry_sw_1"),
}


@register_factor
@fixed_factor('net_income_cash_ratio_1d', {})
class Factor_net_income_cash_ratio_1d(BaseFactor):
    """Operating cash flow divided by net income 1D factor."""
    INPUTS = INPUTS

    name = 'net_income_cash_ratio_1d'
    description = "Operating cash flow divided by net income 1D factor."

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        factor = data['n_cashflow_act'] / data['n_income'].replace(0, pd.NA)

        result = factor.unstack(level="symbol")
        result.index.name = "date"
        result.columns.name = "symbol"
        return result
