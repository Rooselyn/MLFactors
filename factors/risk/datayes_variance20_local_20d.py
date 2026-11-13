"""通联 DataYes／优矿424因子库

公式：var(R,20,ddof=1)。；原目录：Variance20；追踪：DY0162；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'datayes_variance20_local_20d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_variance20_local_20d', {})
class Factor_datayes_variance20_local_20d(PublicFactor):
    name = 'datayes_variance20_local_20d'
    description = 'var(R,20,ddof=1)。；原目录：Variance20；追踪：DY0162；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
