"""通联 DataYes／优矿424因子库

公式：TTM(non_oper_income)−TTM(non_oper_exp)，单位元。；原目录：NonOperatingNPTTM；追踪：DY0381；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'non_oper_income': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'non_oper_income', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'non_oper_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'non_oper_exp', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_non_operating_profit_ttm_pit_4q', 'engine': 'financial', 'expression': 'v0-v1', 'leaves': {'v0': ['financial_income', 'non_oper_income', 'T', 0], 'v1': ['financial_income', 'non_oper_exp', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_non_operating_profit_ttm_pit_4q', {})
class Factor_datayes_non_operating_profit_ttm_pit_4q(PublicFactor):
    name = 'datayes_non_operating_profit_ttm_pit_4q'
    description = 'TTM(non_oper_income)−TTM(non_oper_exp)，单位元。；原目录：NonOperatingNPTTM；追踪：DY0381；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
