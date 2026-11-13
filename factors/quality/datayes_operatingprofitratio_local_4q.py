"""通联 DataYes／优矿424因子库

公式：T(operate_profit)/T(revenue)，比例小数。；原目录：OperatingProfitRatio；追踪：DY0181；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'operate_profit': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'operate_profit', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_operatingprofitratio_local_4q', 'engine': 'financial', 'expression': 'v0/v1', 'leaves': {'v0': ['financial_income', 'operate_profit', 'T', 0], 'v1': ['financial_income', 'revenue', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_operatingprofitratio_local_4q', {})
class Factor_datayes_operatingprofitratio_local_4q(PublicFactor):
    name = 'datayes_operatingprofitratio_local_4q'
    description = 'T(operate_profit)/T(revenue)，比例小数。；原目录：OperatingProfitRatio；追踪：DY0181；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
