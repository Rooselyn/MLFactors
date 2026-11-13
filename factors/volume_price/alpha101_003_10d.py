"""WorldQuant Alpha101

公式：(-1 * correlation(rank(O), rank(V), 10))；原目录：Alpha101_003；追踪：PF00003；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_003_10d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'correlation', [('call', 'rank', [('var', 'O')]), ('call', 'rank', [('var', 'V')]), ('num', 10.0)]))}

@register_factor
@fixed_factor('alpha101_003_10d', {})
class Factor_alpha101_003_10d(PublicFactor):
    name = 'alpha101_003_10d'
    description = '(-1 * correlation(rank(O), rank(V), 10))；原目录：Alpha101_003；追踪：PF00003；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
