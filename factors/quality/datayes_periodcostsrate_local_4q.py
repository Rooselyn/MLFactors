"""通联 DataYes／优矿424因子库

公式：(T(sell_exp)+T(admin_exp)+T(fin_exp))/T(revenue)。；原目录：PeriodCostsRate；追踪：DY0183；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'sell_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'sell_exp', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'admin_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'admin_exp', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'fin_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'fin_exp', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_periodcostsrate_local_4q', 'engine': 'financial', 'expression': '(v0+v1+v2)/v3', 'leaves': {'v0': ['financial_income', 'sell_exp', 'T', 0], 'v1': ['financial_income', 'admin_exp', 'T', 0], 'v2': ['financial_income', 'fin_exp', 'T', 0], 'v3': ['financial_income', 'revenue', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_periodcostsrate_local_4q', {})
class Factor_datayes_periodcostsrate_local_4q(PublicFactor):
    name = 'datayes_periodcostsrate_local_4q'
    description = '(T(sell_exp)+T(admin_exp)+T(fin_exp))/T(revenue)。；原目录：PeriodCostsRate；追踪：DY0183；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
