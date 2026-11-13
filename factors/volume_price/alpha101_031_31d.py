"""WorldQuant Alpha101

公式：((rank(rank(rank(decay_linear((-1 * rank(rank(delta(C, 10)))), 10)))) + rank((-1 * delta(C, 3)))) + sign(scale(correlation(adv20, L, 12))))；原目录：Alpha101_031；追踪：PF00031；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'alpha101_031_31d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '+', ('bin', '+', ('call', 'rank', [('call', 'rank', [('call', 'rank', [('call', 'decay_linear', [('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('call', 'rank', [('call', 'delta', [('var', 'C'), ('num', 10.0)])])])), ('num', 10.0)])])])]), ('call', 'rank', [('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'delta', [('var', 'C'), ('num', 3.0)]))])), ('call', 'sign', [('call', 'scale', [('call', 'correlation', [('var', 'adv20'), ('var', 'L'), ('num', 12.0)])])]))}

@register_factor
@fixed_factor('alpha101_031_31d', {})
class Factor_alpha101_031_31d(PublicFactor):
    name = 'alpha101_031_31d'
    description = '((rank(rank(rank(decay_linear((-1 * rank(rank(delta(C, 10)))), 10)))) + rank((-1 * delta(C, 3)))) + sign(scale(correlation(adv20, L, 12))))；原目录：Alpha101_031；追踪：PF00031；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
