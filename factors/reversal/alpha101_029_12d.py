"""WorldQuant Alpha101

公式：(min(product(rank(rank(scale(log(sum(ts_min(rank(rank((-1 * rank(delta((C - 1), 5))))), 2), 1))))), 1), 5) + ts_rank(delay((-1 * R), 6), 5))；原目录：Alpha101_029；追踪：PF00029；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha101_029_12d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '+', ('call', 'min', [('call', 'product', [('call', 'rank', [('call', 'rank', [('call', 'scale', [('call', 'log', [('call', 'sum', [('call', 'ts_min', [('call', 'rank', [('call', 'rank', [('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('call', 'delta', [('bin', '-', ('var', 'C'), ('num', 1.0)), ('num', 5.0)])]))])]), ('num', 2.0)]), ('num', 1.0)])])])])]), ('num', 1.0)]), ('num', 5.0)]), ('call', 'ts_rank', [('call', 'delay', [('bin', '*', ('unary', '-', ('num', 1.0)), ('var', 'R')), ('num', 6.0)]), ('num', 5.0)]))}

@register_factor
@fixed_factor('alpha101_029_12d', {})
class Factor_alpha101_029_12d(PublicFactor):
    name = 'alpha101_029_12d'
    description = '(min(product(rank(rank(scale(log(sum(ts_min(rank(rank((-1 * rank(delta((C - 1), 5))))), 2), 1))))), 1), 5) + ts_rank(delay((-1 * R), 6), 5))；原目录：Alpha101_029；追踪：PF00029；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
