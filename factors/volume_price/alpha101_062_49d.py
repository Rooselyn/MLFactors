"""WorldQuant Alpha101

公式：((rank(correlation(P, sum(adv20, 22.4101), 9.91009)) < rank(((rank(O) + rank(O)) < (rank(((H + L) / 2)) + rank(H))))) * -1)；原目录：Alpha101_062；追踪：PF00062；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_062_49d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '<', ('call', 'rank', [('call', 'correlation', [('var', 'P'), ('call', 'sum', [('var', 'adv20'), ('num', 22.4101)]), ('num', 9.91009)])]), ('call', 'rank', [('bin', '<', ('bin', '+', ('call', 'rank', [('var', 'O')]), ('call', 'rank', [('var', 'O')])), ('bin', '+', ('call', 'rank', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0))]), ('call', 'rank', [('var', 'H')])))])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_062_49d', {})
class Factor_alpha101_062_49d(PublicFactor):
    name = 'alpha101_062_49d'
    description = '((rank(correlation(P, sum(adv20, 22.4101), 9.91009)) < rank(((rank(O) + rank(O)) < (rank(((H + L) / 2)) + rank(H))))) * -1)；原目录：Alpha101_062；追踪：PF00062；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
