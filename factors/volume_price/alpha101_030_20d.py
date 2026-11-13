"""WorldQuant Alpha101

公式：(((1.0 - rank(((sign((C - delay(C, 1))) + sign((delay(C, 1) - delay(C, 2)))) + sign((delay(C, 2) - delay(C, 3)))))) * sum(V, 5)) / sum(V, 20))；原目录：Alpha101_030；追踪：PF00030；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_030_20d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '/', ('bin', '*', ('bin', '-', ('num', 1.0), ('call', 'rank', [('bin', '+', ('bin', '+', ('call', 'sign', [('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('call', 'sign', [('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 1.0)]), ('call', 'delay', [('var', 'C'), ('num', 2.0)]))])), ('call', 'sign', [('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 2.0)]), ('call', 'delay', [('var', 'C'), ('num', 3.0)]))]))])), ('call', 'sum', [('var', 'V'), ('num', 5.0)])), ('call', 'sum', [('var', 'V'), ('num', 20.0)]))}

@register_factor
@fixed_factor('alpha101_030_20d', {})
class Factor_alpha101_030_20d(PublicFactor):
    name = 'alpha101_030_20d'
    description = '(((1.0 - rank(((sign((C - delay(C, 1))) + sign((delay(C, 1) - delay(C, 2)))) + sign((delay(C, 2) - delay(C, 3)))))) * sum(V, 5)) / sum(V, 20))；原目录：Alpha101_030；追踪：PF00030；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
