"""WorldQuant Alpha101

公式：(rank(correlation(sum(((L * 0.352233) + (P * (1 - 0.352233))), 19.7428), sum(adv40, 19.7428), 6.83313))^rank(correlation(rank(P), rank(V), 5.77492)))；原目录：Alpha101_078；追踪：PF00078；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_078_63d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '^', ('call', 'rank', [('call', 'correlation', [('call', 'sum', [('bin', '+', ('bin', '*', ('var', 'L'), ('num', 0.352233)), ('bin', '*', ('var', 'P'), ('bin', '-', ('num', 1.0), ('num', 0.352233)))), ('num', 19.7428)]), ('call', 'sum', [('var', 'adv40'), ('num', 19.7428)]), ('num', 6.83313)])]), ('call', 'rank', [('call', 'correlation', [('call', 'rank', [('var', 'P')]), ('call', 'rank', [('var', 'V')]), ('num', 5.77492)])]))}

@register_factor
@fixed_factor('alpha101_078_63d', {})
class Factor_alpha101_078_63d(PublicFactor):
    name = 'alpha101_078_63d'
    description = '(rank(correlation(sum(((L * 0.352233) + (P * (1 - 0.352233))), 19.7428), sum(adv40, 19.7428), 6.83313))^rank(correlation(rank(P), rank(V), 5.77492)))；原目录：Alpha101_078；追踪：PF00078；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
