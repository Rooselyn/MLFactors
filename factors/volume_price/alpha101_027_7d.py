"""WorldQuant Alpha101

公式：((0.5 < rank((sum(correlation(rank(V), rank(P), 6), 2) / 2.0))) ? (-1 * 1) : 1)；原目录：Alpha101_027；追踪：PF00027；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_027_7d', 'engine': 'alpha', 'kind': 101, 'tree': ('if', ('bin', '<', ('num', 0.5), ('call', 'rank', [('bin', '/', ('call', 'sum', [('call', 'correlation', [('call', 'rank', [('var', 'V')]), ('call', 'rank', [('var', 'P')]), ('num', 6.0)]), ('num', 2.0)]), ('num', 2.0))])), ('bin', '*', ('unary', '-', ('num', 1.0)), ('num', 1.0)), ('num', 1.0))}

@register_factor
@fixed_factor('alpha101_027_7d', {})
class Factor_alpha101_027_7d(PublicFactor):
    name = 'alpha101_027_7d'
    description = '((0.5 < rank((sum(correlation(rank(V), rank(P), 6), 2) / 2.0))) ? (-1 * 1) : 1)；原目录：Alpha101_027；追踪：PF00027；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
