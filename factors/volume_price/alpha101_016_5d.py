"""WorldQuant Alpha101

公式：(-1 * rank(covariance(rank(H), rank(V), 5)))；原目录：Alpha101_016；追踪：PF00016；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_016_5d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('call', 'covariance', [('call', 'rank', [('var', 'H')]), ('call', 'rank', [('var', 'V')]), ('num', 5.0)])]))}

@register_factor
@fixed_factor('alpha101_016_5d', {})
class Factor_alpha101_016_5d(PublicFactor):
    name = 'alpha101_016_5d'
    description = '(-1 * rank(covariance(rank(H), rank(V), 5)))；原目录：Alpha101_016；追踪：PF00016；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
