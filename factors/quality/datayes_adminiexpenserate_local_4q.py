"""通联 DataYes／优矿424因子库

公式：T(admin_exp)/T(total_revenue)，比例小数。；原目录：AdminiExpenseRate；追踪：DY0164；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'admin_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'admin_exp', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'total_revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_adminiexpenserate_local_4q', 'engine': 'financial', 'expression': 'v0/v1', 'leaves': {'v0': ['financial_income', 'admin_exp', 'T', 0], 'v1': ['financial_income', 'total_revenue', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_adminiexpenserate_local_4q', {})
class Factor_datayes_adminiexpenserate_local_4q(PublicFactor):
    name = 'datayes_adminiexpenserate_local_4q'
    description = 'T(admin_exp)/T(total_revenue)，比例小数。；原目录：AdminiExpenseRate；追踪：DY0164；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
