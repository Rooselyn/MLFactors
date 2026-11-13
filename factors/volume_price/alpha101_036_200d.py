"""WorldQuant Alpha101

公式：(((((2.21 * rank(correlation((C - O), delay(V, 1), 15))) + (0.7 * rank((O - C)))) + (0.73 * rank(Ts_Rank(delay((-1 * R), 6), 5)))) + rank(abs(correlation(P, adv20, 6)))) + (0.6 * rank((((sum(C, 200) / 200) - O) * (C - O)))))；原目录：Alpha101_036；追踪：PF00036；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_036_200d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '+', ('bin', '+', ('bin', '+', ('bin', '+', ('bin', '*', ('num', 2.21), ('call', 'rank', [('call', 'correlation', [('bin', '-', ('var', 'C'), ('var', 'O')), ('call', 'delay', [('var', 'V'), ('num', 1.0)]), ('num', 15.0)])])), ('bin', '*', ('num', 0.7), ('call', 'rank', [('bin', '-', ('var', 'O'), ('var', 'C'))]))), ('bin', '*', ('num', 0.73), ('call', 'rank', [('call', 'ts_rank', [('call', 'delay', [('bin', '*', ('unary', '-', ('num', 1.0)), ('var', 'R')), ('num', 6.0)]), ('num', 5.0)])]))), ('call', 'rank', [('call', 'abs', [('call', 'correlation', [('var', 'P'), ('var', 'adv20'), ('num', 6.0)])])])), ('bin', '*', ('num', 0.6), ('call', 'rank', [('bin', '*', ('bin', '-', ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 200.0)]), ('num', 200.0)), ('var', 'O')), ('bin', '-', ('var', 'C'), ('var', 'O')))])))}

@register_factor
@fixed_factor('alpha101_036_200d', {})
class Factor_alpha101_036_200d(PublicFactor):
    name = 'alpha101_036_200d'
    description = '(((((2.21 * rank(correlation((C - O), delay(V, 1), 15))) + (0.7 * rank((O - C)))) + (0.73 * rank(Ts_Rank(delay((-1 * R), 6), 5)))) + rank(abs(correlation(P, adv20, 6)))) + (0.6 * rank((((sum(C, 200) / 200) - O) * (C - O)))))；原目录：Alpha101_036；追踪：PF00036；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
