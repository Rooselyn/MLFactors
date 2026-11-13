"""WorldQuant Alpha101

公式：((rank(Log(product(rank((rank(correlation(P, sum(adv10, 49.6054), 8.47743))^4)), 14.9655))) < rank(correlation(rank(P), rank(V), 5.07914))) * -1)；原目录：Alpha101_081；追踪：PF00081；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_081_78d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '<', ('call', 'rank', [('call', 'log', [('call', 'product', [('call', 'rank', [('bin', '^', ('call', 'rank', [('call', 'correlation', [('var', 'P'), ('call', 'sum', [('var', 'adv10'), ('num', 49.6054)]), ('num', 8.47743)])]), ('num', 4.0))]), ('num', 14.9655)])])]), ('call', 'rank', [('call', 'correlation', [('call', 'rank', [('var', 'P')]), ('call', 'rank', [('var', 'V')]), ('num', 5.07914)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_081_78d', {})
class Factor_alpha101_081_78d(PublicFactor):
    name = 'alpha101_081_78d'
    description = '((rank(Log(product(rank((rank(correlation(P, sum(adv10, 49.6054), 8.47743))^4)), 14.9655))) < rank(correlation(rank(P), rank(V), 5.07914))) * -1)；原目录：Alpha101_081；追踪：PF00081；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
