"""WorldQuant Alpha101

公式：((rank(decay_linear(delta(IndNeutralize(((L * 0.721001) + (P * (1 - 0.721001))), SW2), 3.3705), 20.4523)) - Ts_Rank(decay_linear(Ts_Rank(correlation(Ts_Rank(L, 7.87871), Ts_Rank(adv60, 17.255), 4.97547), 18.5925), 15.7152), 6.71659)) * -1)；原目录：Alpha101_097；追踪：PF00097；[来源](https://arxiv.org/pdf/1601.00991)。
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
    'industry_sw_2': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_2'),
}
SPEC = {'name': 'alpha101_097_115d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '-', ('call', 'rank', [('call', 'decay_linear', [('call', 'delta', [('call', 'indneutralize', [('bin', '+', ('bin', '*', ('var', 'L'), ('num', 0.721001)), ('bin', '*', ('var', 'P'), ('bin', '-', ('num', 1.0), ('num', 0.721001)))), ('var', 'SW2')]), ('num', 3.3705)]), ('num', 20.4523)])]), ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'ts_rank', [('call', 'correlation', [('call', 'ts_rank', [('var', 'L'), ('num', 7.87871)]), ('call', 'ts_rank', [('var', 'adv60'), ('num', 17.255)]), ('num', 4.97547)]), ('num', 18.5925)]), ('num', 15.7152)]), ('num', 6.71659)])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_097_115d', {})
class Factor_alpha101_097_115d(PublicFactor):
    name = 'alpha101_097_115d'
    description = '((rank(decay_linear(delta(IndNeutralize(((L * 0.721001) + (P * (1 - 0.721001))), SW2), 3.3705), 20.4523)) - Ts_Rank(decay_linear(Ts_Rank(correlation(Ts_Rank(L, 7.87871), Ts_Rank(adv60, 17.255), 4.97547), 18.5925), 15.7152), 6.71659)) * -1)；原目录：Alpha101_097；追踪：PF00097；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
