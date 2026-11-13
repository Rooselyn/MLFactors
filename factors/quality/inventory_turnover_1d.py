"""inventory_turnover_1d：质量；输入来源由本文件维护。"""
from __future__ import annotations

from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
import pandas as pd
from factors.base import BaseFactor


# 输入按年/月分区动态发现；字段名直接采用Parquet物理列名，价格统一后复权。
# 财报使用合并累计报表(report_type=1)，仅从公告后交易日起可用。
INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "close_hfq"),
    'cost_revenue': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "oper_cost", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),), expression='oper_cost / revenue'),
    'revenue': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", "revenue", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'inventories': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", "inventories", date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'industry_sw_1': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", "industry_sw_1"),
}


@register_factor
@fixed_factor('inventory_turnover_1d', {})
class Factor_inventory_turnover_1d(BaseFactor):
    """Inventory turnover 1D factor."""
    INPUTS = INPUTS

    name = 'inventory_turnover_1d'
    description = "Inventory turnover 1D factor."

    def generate_signals(
        self,
        data: pd.DataFrame,
        constituents: dict[str, set[str]] | None = None,
    ) -> pd.DataFrame:
        # 源 CSV 的 cost_revenue 是“营业成本 / 营业收入”比例，先还原为
        # 营业成本金额，再计算存货周转率，以对齐平台侧的金额口径。
        cost_of_revenue = data["cost_revenue"] * data["revenue"]
        factor = cost_of_revenue / data['inventories'].replace(0, pd.NA)

        result = factor.unstack(level="symbol")
        result.index.name = "date"
        result.columns.name = "symbol"
        return result
