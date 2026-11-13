"""通联 DataYes／优矿424因子库

公式：(QY(non_oper_income)−QY(non_oper_exp))/QY(total_profit)。；原目录：NetNonOIToTPLatest；追踪：DY0176；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'non_oper_income': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'non_oper_income', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'non_oper_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'non_oper_exp', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_profit': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'total_profit', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_netnonoitotplatest_local_1q', 'engine': 'financial', 'expression': '(v0-v1)/v2', 'leaves': {'v0': ['financial_income', 'non_oper_income', 'QY', 0], 'v1': ['financial_income', 'non_oper_exp', 'QY', 0], 'v2': ['financial_income', 'total_profit', 'QY', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_netnonoitotplatest_local_1q', {})
class Factor_datayes_netnonoitotplatest_local_1q(PublicFactor):
    name = 'datayes_netnonoitotplatest_local_1q'
    description = '(QY(non_oper_income)−QY(non_oper_exp))/QY(total_profit)。；原目录：NetNonOIToTPLatest；追踪：DY0176；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
