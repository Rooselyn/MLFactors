"""WorldQuant Alpha101

公式：((rank(ts_max(delta(IndNeutralize(P, SW2), 2.72412), 4.79344))^Ts_Rank(correlation(((C * 0.490655) + (P * (1 - 0.490655))), adv20, 4.92416), 9.0615)) * -1)；原目录：Alpha101_069；追踪：PF00069；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
    'industry_sw_2': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_2'),
}
SPEC = {'name': 'alpha101_069_31d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '^', ('call', 'rank', [('call', 'ts_max', [('call', 'delta', [('call', 'indneutralize', [('var', 'P'), ('var', 'SW2')]), ('num', 2.72412)]), ('num', 4.79344)])]), ('call', 'ts_rank', [('call', 'correlation', [('bin', '+', ('bin', '*', ('var', 'C'), ('num', 0.490655)), ('bin', '*', ('var', 'P'), ('bin', '-', ('num', 1.0), ('num', 0.490655)))), ('var', 'adv20'), ('num', 4.92416)]), ('num', 9.0615)])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_069_31d', {})
class Factor_alpha101_069_31d(PublicFactor):
    name = 'alpha101_069_31d'
    description = '((rank(ts_max(delta(IndNeutralize(P, SW2), 2.72412), 4.79344))^Ts_Rank(correlation(((C * 0.490655) + (P * (1 - 0.490655))), adv20, 4.92416), 9.0615)) * -1)；原目录：Alpha101_069；追踪：PF00069；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
