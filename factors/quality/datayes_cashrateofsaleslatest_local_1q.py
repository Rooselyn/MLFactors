"""通联 DataYes／优矿424因子库

公式：QY(n_cashflow_act)/QY(revenue)，同一期YTD相除。；原目录：CashRateOfSalesLatest；追踪：DY0400；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'n_cashflow_act': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_cashflow_act', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_cashrateofsaleslatest_local_1q', 'engine': 'financial', 'expression': 'v0/v1', 'leaves': {'v0': ['financial_cash_flow', 'n_cashflow_act', 'QY', 0], 'v1': ['financial_income', 'revenue', 'QY', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_cashrateofsaleslatest_local_1q', {})
class Factor_datayes_cashrateofsaleslatest_local_1q(PublicFactor):
    name = 'datayes_cashrateofsaleslatest_local_1q'
    description = 'QY(n_cashflow_act)/QY(revenue)，同一期YTD相除。；原目录：CashRateOfSalesLatest；追踪：DY0400；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
