"""WorldQuant Alpha101

公式：((((delta((sum(C, 100) / 100), 100) / delay(C, 100)) < 0.05) || ((delta((sum(C, 100) / 100), 100) / delay(C, 100)) == 0.05)) ? (-1 * (C - ts_min(C, 100))) : (-1 * delta(C, 3)))；原目录：Alpha101_024；追踪：PF00024；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha101_024_200d', 'engine': 'alpha', 'kind': 101, 'tree': ('if', ('bin', '||', ('bin', '<', ('bin', '/', ('call', 'delta', [('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 100.0)]), ('num', 100.0)), ('num', 100.0)]), ('call', 'delay', [('var', 'C'), ('num', 100.0)])), ('num', 0.05)), ('bin', '==', ('bin', '/', ('call', 'delta', [('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 100.0)]), ('num', 100.0)), ('num', 100.0)]), ('call', 'delay', [('var', 'C'), ('num', 100.0)])), ('num', 0.05))), ('bin', '*', ('unary', '-', ('num', 1.0)), ('bin', '-', ('var', 'C'), ('call', 'ts_min', [('var', 'C'), ('num', 100.0)]))), ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'delta', [('var', 'C'), ('num', 3.0)])))}

@register_factor
@fixed_factor('alpha101_024_200d', {})
class Factor_alpha101_024_200d(PublicFactor):
    name = 'alpha101_024_200d'
    description = '((((delta((sum(C, 100) / 100), 100) / delay(C, 100)) < 0.05) || ((delta((sum(C, 100) / 100), 100) / delay(C, 100)) == 0.05)) ? (-1 * (C - ts_min(C, 100))) : (-1 * delta(C, 3)))；原目录：Alpha101_024；追踪：PF00024；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
