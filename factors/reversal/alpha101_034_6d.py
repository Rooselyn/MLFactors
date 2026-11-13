"""WorldQuant Alpha101

公式：rank(((1 - rank((stddev(R, 2) / stddev(R, 5)))) + (1 - rank(delta(C, 1)))))；原目录：Alpha101_034；追踪：PF00034；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha101_034_6d', 'engine': 'alpha', 'kind': 101, 'tree': ('call', 'rank', [('bin', '+', ('bin', '-', ('num', 1.0), ('call', 'rank', [('bin', '/', ('call', 'stddev', [('var', 'R'), ('num', 2.0)]), ('call', 'stddev', [('var', 'R'), ('num', 5.0)]))])), ('bin', '-', ('num', 1.0), ('call', 'rank', [('call', 'delta', [('var', 'C'), ('num', 1.0)])])))])}

@register_factor
@fixed_factor('alpha101_034_6d', {})
class Factor_alpha101_034_6d(PublicFactor):
    name = 'alpha101_034_6d'
    description = 'rank(((1 - rank((stddev(R, 2) / stddev(R, 5)))) + (1 - rank(delta(C, 1)))))；原目录：Alpha101_034；追踪：PF00034；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
