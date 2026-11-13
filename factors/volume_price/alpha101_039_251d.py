"""WorldQuant Alpha101

公式：((-1 * rank((delta(C, 7) * (1 - rank(decay_linear((V / adv20), 9)))))) * (1 + rank(sum(R, 250))))；原目录：Alpha101_039；追踪：PF00039；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'alpha101_039_251d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('bin', '*', ('call', 'delta', [('var', 'C'), ('num', 7.0)]), ('bin', '-', ('num', 1.0), ('call', 'rank', [('call', 'decay_linear', [('bin', '/', ('var', 'V'), ('var', 'adv20')), ('num', 9.0)])])))])), ('bin', '+', ('num', 1.0), ('call', 'rank', [('call', 'sum', [('var', 'R'), ('num', 250.0)])])))}

@register_factor
@fixed_factor('alpha101_039_251d', {})
class Factor_alpha101_039_251d(PublicFactor):
    name = 'alpha101_039_251d'
    description = '((-1 * rank((delta(C, 7) * (1 - rank(decay_linear((V / adv20), 9)))))) * (1 + rank(sum(R, 250))))；原目录：Alpha101_039；追踪：PF00039；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
