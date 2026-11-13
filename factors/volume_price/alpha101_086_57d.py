"""WorldQuant Alpha101

公式：((Ts_Rank(correlation(C, sum(adv20, 14.7444), 6.00049), 20.4195) < rank(((O + C) - (P + O)))) * -1)；原目录：Alpha101_086；追踪：PF00086；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_086_57d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '<', ('call', 'ts_rank', [('call', 'correlation', [('var', 'C'), ('call', 'sum', [('var', 'adv20'), ('num', 14.7444)]), ('num', 6.00049)]), ('num', 20.4195)]), ('call', 'rank', [('bin', '-', ('bin', '+', ('var', 'O'), ('var', 'C')), ('bin', '+', ('var', 'P'), ('var', 'O')))])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_086_57d', {})
class Factor_alpha101_086_57d(PublicFactor):
    name = 'alpha101_086_57d'
    description = '((Ts_Rank(correlation(C, sum(adv20, 14.7444), 6.00049), 20.4195) < rank(((O + C) - (P + O)))) * -1)；原目录：Alpha101_086；追踪：PF00086；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
