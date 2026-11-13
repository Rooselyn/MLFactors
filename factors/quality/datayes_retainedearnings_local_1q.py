"""通联 DataYes／优矿424因子库

公式：B(surplus_rese)+B(undistr_porfit)，留存收益元；不加资本公积。；原目录：RetainedEarnings；追踪：DY0384；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'surplus_rese': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'surplus_rese', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'undistr_porfit': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'undistr_porfit', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_retainedearnings_local_1q', 'engine': 'financial', 'expression': 'v0+v1', 'leaves': {'v0': ['financial_balance_sheet', 'surplus_rese', 'B', 0], 'v1': ['financial_balance_sheet', 'undistr_porfit', 'B', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_retainedearnings_local_1q', {})
class Factor_datayes_retainedearnings_local_1q(PublicFactor):
    name = 'datayes_retainedearnings_local_1q'
    description = 'B(surplus_rese)+B(undistr_porfit)，留存收益元；不加资本公积。；原目录：RetainedEarnings；追踪：DY0384；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
