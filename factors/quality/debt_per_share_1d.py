"""debt_per_share_1d：质量；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
    'total_debt': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "st_borr", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),), expression='sum_available(st_borr, st_bonds_payable, lt_borr, bond_payable, lt_payable, lease_liab, non_cur_liab_due_1y)'),
    'total_share': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "total_share", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'industry_sw_1': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "industry_sw_1"),
}


@register_factor
@fixed_factor('debt_per_share_1d', {})
class Factor_debt_per_share_1d(BaseFactor):
    """Debt per share 1D factor."""
    INPUTS = INPUTS

    name = 'debt_per_share_1d'
    description = "Debt per share 1D factor."

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        factor = data["total_debt"] / data['total_share'].replace(0, pd.NA)

        result = factor.unstack(level="symbol")
        result.index.name = "date"
        result.columns.name = "symbol"
        return result
