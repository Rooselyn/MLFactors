"""WorldQuant Alpha101

公式：(-1 * rank(covariance(rank(C), rank(V), 5)))；原目录：Alpha101_013；追踪：PF00013；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_013_5d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('call', 'covariance', [('call', 'rank', [('var', 'C')]), ('call', 'rank', [('var', 'V')]), ('num', 5.0)])]))}

@register_factor
@fixed_factor('alpha101_013_5d', {})
class Factor_alpha101_013_5d(PublicFactor):
    name = 'alpha101_013_5d'
    description = '(-1 * rank(covariance(rank(C), rank(V), 5)))；原目录：Alpha101_013；追踪：PF00013；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
