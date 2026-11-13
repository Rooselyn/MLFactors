"""通联 DataYes／优矿424因子库

公式：mean(A,6)，A=amount×1000元。；原目录：TVMA6；追踪：DY0013；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'datayes_amount_mean_6d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_amount_mean_6d', {})
class Factor_datayes_amount_mean_6d(PublicFactor):
    name = 'datayes_amount_mean_6d'
    description = 'mean(A,6)，A=amount×1000元。；原目录：TVMA6；追踪：DY0013；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
