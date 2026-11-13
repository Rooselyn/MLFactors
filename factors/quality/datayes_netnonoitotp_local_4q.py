"""通联 DataYes／优矿424因子库

公式：(T(non_oper_income)−T(non_oper_exp))/T(total_profit)。；原目录：NetNonOIToTP；追踪：DY0175；[来源](https://uqer.datayes.com/help/appendixFactors/)。
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
SPEC = {'name': 'datayes_netnonoitotp_local_4q', 'engine': 'financial', 'expression': '(v0-v1)/v2', 'leaves': {'v0': ['financial_income', 'non_oper_income', 'T', 0], 'v1': ['financial_income', 'non_oper_exp', 'T', 0], 'v2': ['financial_income', 'total_profit', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_netnonoitotp_local_4q', {})
class Factor_datayes_netnonoitotp_local_4q(PublicFactor):
    name = 'datayes_netnonoitotp_local_4q'
    description = '(T(non_oper_income)−T(non_oper_exp))/T(total_profit)。；原目录：NetNonOIToTP；追踪：DY0175；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
