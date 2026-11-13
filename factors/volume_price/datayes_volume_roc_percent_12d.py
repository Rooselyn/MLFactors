"""通联 DataYes／优矿424因子库

公式：100×(vol[t]/vol[t−12]−1)。；原目录：VROC12；追踪：DY0031；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'datayes_volume_roc_percent_12d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_volume_roc_percent_12d', {})
class Factor_datayes_volume_roc_percent_12d(PublicFactor):
    name = 'datayes_volume_roc_percent_12d'
    description = '100×(vol[t]/vol[t−12]−1)。；原目录：VROC12；追踪：DY0031；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
