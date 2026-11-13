"""WorldQuant Alpha101

公式：((-1 * sign(((C - delay(C, 7)) + delta(C, 7)))) * (1 + rank((1 + sum(R, 250)))))；原目录：Alpha101_019；追踪：PF00019；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha101_019_251d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'sign', [('bin', '+', ('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 7.0)])), ('call', 'delta', [('var', 'C'), ('num', 7.0)]))])), ('bin', '+', ('num', 1.0), ('call', 'rank', [('bin', '+', ('num', 1.0), ('call', 'sum', [('var', 'R'), ('num', 250.0)]))])))}

@register_factor
@fixed_factor('alpha101_019_251d', {})
class Factor_alpha101_019_251d(PublicFactor):
    name = 'alpha101_019_251d'
    description = '((-1 * sign(((C - delay(C, 7)) + delta(C, 7)))) * (1 + rank((1 + sum(R, 250)))))；原目录：Alpha101_019；追踪：PF00019；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
