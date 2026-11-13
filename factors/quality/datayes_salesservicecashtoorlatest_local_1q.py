"""通联 DataYes／优矿424因子库

公式：QY(c_fr_sale_sg)/QY(revenue)，同一期YTD相除。；原目录：SalesServiceCashToORLatest；追踪：DY0411；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'c_fr_sale_sg': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'c_fr_sale_sg', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_salesservicecashtoorlatest_local_1q', 'engine': 'financial', 'expression': 'v0/v1', 'leaves': {'v0': ['financial_cash_flow', 'c_fr_sale_sg', 'QY', 0], 'v1': ['financial_income', 'revenue', 'QY', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_salesservicecashtoorlatest_local_1q', {})
class Factor_datayes_salesservicecashtoorlatest_local_1q(PublicFactor):
    name = 'datayes_salesservicecashtoorlatest_local_1q'
    description = 'QY(c_fr_sale_sg)/QY(revenue)，同一期YTD相除。；原目录：SalesServiceCashToORLatest；追踪：DY0411；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
