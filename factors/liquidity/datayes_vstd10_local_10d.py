"""通联 DataYes／优矿424因子库

公式：std(vol×100,10,ddof=1)，单位股。；原目录：VSTD10；追踪：DY0033；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'datayes_vstd10_local_10d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_vstd10_local_10d', {})
class Factor_datayes_vstd10_local_10d(PublicFactor):
    name = 'datayes_vstd10_local_10d'
    description = 'std(vol×100,10,ddof=1)，单位股。；原目录：VSTD10；追踪：DY0033；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
