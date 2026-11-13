"""通联 DataYes／优矿424因子库

公式：std(vol×100,20,ddof=1)，单位股。；原目录：VSTD20；追踪：DY0034；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'datayes_vstd20_local_20d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_vstd20_local_20d', {})
class Factor_datayes_vstd20_local_20d(PublicFactor):
    name = 'datayes_vstd20_local_20d'
    description = 'std(vol×100,20,ddof=1)，单位股。；原目录：VSTD20；追踪：DY0034；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
