"""WorldQuant Alpha101

公式：(-1 * correlation(rank(delta(log(V), 2)), rank(((C - O) / O)), 6))；原目录：Alpha101_002；追踪：PF00002；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_002_8d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'correlation', [('call', 'rank', [('call', 'delta', [('call', 'log', [('var', 'V')]), ('num', 2.0)])]), ('call', 'rank', [('bin', '/', ('bin', '-', ('var', 'C'), ('var', 'O')), ('var', 'O'))]), ('num', 6.0)]))}

@register_factor
@fixed_factor('alpha101_002_8d', {})
class Factor_alpha101_002_8d(PublicFactor):
    name = 'alpha101_002_8d'
    description = '(-1 * correlation(rank(delta(log(V), 2)), rank(((C - O) / O)), 6))；原目录：Alpha101_002；追踪：PF00002；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
