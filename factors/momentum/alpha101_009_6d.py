"""WorldQuant Alpha101

公式：((0 < ts_min(delta(C, 1), 5)) ? delta(C, 1) : ((ts_max(delta(C, 1), 5) < 0) ? delta(C, 1) : (-1 * delta(C, 1))))；原目录：Alpha101_009；追踪：PF00009；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha101_009_6d', 'engine': 'alpha', 'kind': 101, 'tree': ('if', ('bin', '<', ('num', 0.0), ('call', 'ts_min', [('call', 'delta', [('var', 'C'), ('num', 1.0)]), ('num', 5.0)])), ('call', 'delta', [('var', 'C'), ('num', 1.0)]), ('if', ('bin', '<', ('call', 'ts_max', [('call', 'delta', [('var', 'C'), ('num', 1.0)]), ('num', 5.0)]), ('num', 0.0)), ('call', 'delta', [('var', 'C'), ('num', 1.0)]), ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'delta', [('var', 'C'), ('num', 1.0)]))))}

@register_factor
@fixed_factor('alpha101_009_6d', {})
class Factor_alpha101_009_6d(PublicFactor):
    name = 'alpha101_009_6d'
    description = '((0 < ts_min(delta(C, 1), 5)) ? delta(C, 1) : ((ts_max(delta(C, 1), 5) < 0) ? delta(C, 1) : (-1 * delta(C, 1))))；原目录：Alpha101_009；追踪：PF00009；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
