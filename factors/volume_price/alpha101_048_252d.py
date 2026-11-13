"""WorldQuant Alpha101

公式：(indneutralize(((correlation(delta(C, 1), delta(delay(C, 1), 1), 250) * delta(C, 1)) / C), SW3) / sum(((delta(C, 1) / delay(C, 1))^2), 250))；原目录：Alpha101_048；追踪：PF00048；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'industry_sw_3': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_3'),
}
SPEC = {'name': 'alpha101_048_252d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '/', ('call', 'indneutralize', [('bin', '/', ('bin', '*', ('call', 'correlation', [('call', 'delta', [('var', 'C'), ('num', 1.0)]), ('call', 'delta', [('call', 'delay', [('var', 'C'), ('num', 1.0)]), ('num', 1.0)]), ('num', 250.0)]), ('call', 'delta', [('var', 'C'), ('num', 1.0)])), ('var', 'C')), ('var', 'SW3')]), ('call', 'sum', [('bin', '^', ('bin', '/', ('call', 'delta', [('var', 'C'), ('num', 1.0)]), ('call', 'delay', [('var', 'C'), ('num', 1.0)])), ('num', 2.0)), ('num', 250.0)]))}

@register_factor
@fixed_factor('alpha101_048_252d', {})
class Factor_alpha101_048_252d(PublicFactor):
    name = 'alpha101_048_252d'
    description = '(indneutralize(((correlation(delta(C, 1), delta(delay(C, 1), 1), 250) * delta(C, 1)) / C), SW3) / sum(((delta(C, 1) / delay(C, 1))^2), 250))；原目录：Alpha101_048；追踪：PF00048；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
