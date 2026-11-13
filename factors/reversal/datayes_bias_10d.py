"""通联 DataYes／优矿424因子库

公式：100×(X[t]/mean(X,10)−1)，X=close×adj_factor；前后复权尺度对该比率相消。；原目录：BIAS10；追踪：DY0247；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'datayes_bias_10d', 'engine': 'market'}

@register_factor
@fixed_factor('datayes_bias_10d', {})
class Factor_datayes_bias_10d(PublicFactor):
    name = 'datayes_bias_10d'
    description = '100×(X[t]/mean(X,10)−1)，X=close×adj_factor；前后复权尺度对该比率相消。；原目录：BIAS10；追踪：DY0247；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
