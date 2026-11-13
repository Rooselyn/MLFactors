"""WorldQuant Alpha101

公式：(-1 * ((rank((sum(delay(C, 5), 20) / 20)) * correlation(C, V, 2)) * rank(correlation(sum(C, 5), sum(C, 20), 2))))；原目录：Alpha101_045；追踪：PF00045；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_045_25d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('bin', '*', ('bin', '*', ('call', 'rank', [('bin', '/', ('call', 'sum', [('call', 'delay', [('var', 'C'), ('num', 5.0)]), ('num', 20.0)]), ('num', 20.0))]), ('call', 'correlation', [('var', 'C'), ('var', 'V'), ('num', 2.0)])), ('call', 'rank', [('call', 'correlation', [('call', 'sum', [('var', 'C'), ('num', 5.0)]), ('call', 'sum', [('var', 'C'), ('num', 20.0)]), ('num', 2.0)])])))}

@register_factor
@fixed_factor('alpha101_045_25d', {})
class Factor_alpha101_045_25d(PublicFactor):
    name = 'alpha101_045_25d'
    description = '(-1 * ((rank((sum(delay(C, 5), 20) / 20)) * correlation(C, V, 2)) * rank(correlation(sum(C, 5), sum(C, 20), 2))))；原目录：Alpha101_045；追踪：PF00045；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
