"""WorldQuant Alpha101

公式：(sign(delta(V, 1)) * (-1 * delta(C, 1)))；原目录：Alpha101_012；追踪：PF00012；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_012_2d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('call', 'sign', [('call', 'delta', [('var', 'V'), ('num', 1.0)])]), ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'delta', [('var', 'C'), ('num', 1.0)])))}

@register_factor
@fixed_factor('alpha101_012_2d', {})
class Factor_alpha101_012_2d(PublicFactor):
    name = 'alpha101_012_2d'
    description = '(sign(delta(V, 1)) * (-1 * delta(C, 1)))；原目录：Alpha101_012；追踪：PF00012；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
