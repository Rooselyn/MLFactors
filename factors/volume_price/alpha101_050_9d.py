"""WorldQuant Alpha101

公式：(-1 * ts_max(rank(correlation(rank(V), rank(P), 5)), 5))；原目录：Alpha101_050；追踪：PF00050；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_050_9d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'ts_max', [('call', 'rank', [('call', 'correlation', [('call', 'rank', [('var', 'V')]), ('call', 'rank', [('var', 'P')]), ('num', 5.0)])]), ('num', 5.0)]))}

@register_factor
@fixed_factor('alpha101_050_9d', {})
class Factor_alpha101_050_9d(PublicFactor):
    name = 'alpha101_050_9d'
    description = '(-1 * ts_max(rank(correlation(rank(V), rank(P), 5)), 5))；原目录：Alpha101_050；追踪：PF00050；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
