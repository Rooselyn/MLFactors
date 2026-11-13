"""WorldQuant Alpha101

公式：((rank(correlation(C, sum(adv30, 37.4843), 15.1365)) < rank(correlation(rank(((H * 0.0261661) + (P * (1 - 0.0261661)))), rank(V), 11.4791))) * -1)；原目录：Alpha101_074；追踪：PF00074；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_074_80d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '<', ('call', 'rank', [('call', 'correlation', [('var', 'C'), ('call', 'sum', [('var', 'adv30'), ('num', 37.4843)]), ('num', 15.1365)])]), ('call', 'rank', [('call', 'correlation', [('call', 'rank', [('bin', '+', ('bin', '*', ('var', 'H'), ('num', 0.0261661)), ('bin', '*', ('var', 'P'), ('bin', '-', ('num', 1.0), ('num', 0.0261661))))]), ('call', 'rank', [('var', 'V')]), ('num', 11.4791)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_074_80d', {})
class Factor_alpha101_074_80d(PublicFactor):
    name = 'alpha101_074_80d'
    description = '((rank(correlation(C, sum(adv30, 37.4843), 15.1365)) < rank(correlation(rank(((H * 0.0261661) + (P * (1 - 0.0261661)))), rank(V), 11.4791))) * -1)；原目录：Alpha101_074；追踪：PF00074；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
