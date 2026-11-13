"""WorldQuant Alpha101

公式：(rank(delta(IndNeutralize(((C * 0.60733) + (O * (1 - 0.60733))), SW1), 1.23438)) < rank(correlation(Ts_Rank(P, 3.60973), Ts_Rank(adv150, 9.18637), 14.6644)))；原目录：Alpha101_079；追踪：PF00079；[来源](https://arxiv.org/pdf/1601.00991)。
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
    'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1'),
}
SPEC = {'name': 'alpha101_079_171d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '<', ('call', 'rank', [('call', 'delta', [('call', 'indneutralize', [('bin', '+', ('bin', '*', ('var', 'C'), ('num', 0.60733)), ('bin', '*', ('var', 'O'), ('bin', '-', ('num', 1.0), ('num', 0.60733)))), ('var', 'SW1')]), ('num', 1.23438)])]), ('call', 'rank', [('call', 'correlation', [('call', 'ts_rank', [('var', 'P'), ('num', 3.60973)]), ('call', 'ts_rank', [('var', 'adv150'), ('num', 9.18637)]), ('num', 14.6644)])]))}

@register_factor
@fixed_factor('alpha101_079_171d', {})
class Factor_alpha101_079_171d(PublicFactor):
    name = 'alpha101_079_171d'
    description = '(rank(delta(IndNeutralize(((C * 0.60733) + (O * (1 - 0.60733))), SW1), 1.23438)) < rank(correlation(Ts_Rank(P, 3.60973), Ts_Rank(adv150, 9.18637), 14.6644)))；原目录：Alpha101_079；追踪：PF00079；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
