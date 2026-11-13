"""WorldQuant Alpha101

公式：((rank(decay_linear(delta(P, 3.51013), 7.23052)) + Ts_Rank(decay_linear(((((L * 0.96633) + (L * (1 - 0.96633))) - P) / (O - ((H + L) / 2))), 11.4157), 6.72611)) * -1)；原目录：Alpha101_066；追踪：PF00066；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_066_16d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '+', ('call', 'rank', [('call', 'decay_linear', [('call', 'delta', [('var', 'P'), ('num', 3.51013)]), ('num', 7.23052)])]), ('call', 'ts_rank', [('call', 'decay_linear', [('bin', '/', ('bin', '-', ('bin', '+', ('bin', '*', ('var', 'L'), ('num', 0.96633)), ('bin', '*', ('var', 'L'), ('bin', '-', ('num', 1.0), ('num', 0.96633)))), ('var', 'P')), ('bin', '-', ('var', 'O'), ('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)))), ('num', 11.4157)]), ('num', 6.72611)])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_066_16d', {})
class Factor_alpha101_066_16d(PublicFactor):
    name = 'alpha101_066_16d'
    description = '((rank(decay_linear(delta(P, 3.51013), 7.23052)) + Ts_Rank(decay_linear(((((L * 0.96633) + (L * (1 - 0.96633))) - P) / (O - ((H + L) / 2))), 11.4157), 6.72611)) * -1)；原目录：Alpha101_066；追踪：PF00066；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
