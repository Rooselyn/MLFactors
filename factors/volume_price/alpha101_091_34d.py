"""WorldQuant Alpha101

公式：((Ts_Rank(decay_linear(decay_linear(correlation(IndNeutralize(C, SW2), V, 9.74928), 16.398), 3.83219), 4.8667) - rank(decay_linear(correlation(P, adv30, 4.01303), 2.6809))) * -1)；原目录：Alpha101_091；追踪：PF00091；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_091_34d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '-', ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'decay_linear', [('call', 'correlation', [('call', 'indneutralize', [('var', 'C'), ('var', 'SW2')]), ('var', 'V'), ('num', 9.74928)]), ('num', 16.398)]), ('num', 3.83219)]), ('num', 4.8667)]), ('call', 'rank', [('call', 'decay_linear', [('call', 'correlation', [('var', 'P'), ('var', 'adv30'), ('num', 4.01303)]), ('num', 2.6809)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_091_34d', {})
class Factor_alpha101_091_34d(PublicFactor):
    name = 'alpha101_091_34d'
    description = '((Ts_Rank(decay_linear(decay_linear(correlation(IndNeutralize(C, SW2), V, 9.74928), 16.398), 3.83219), 4.8667) - rank(decay_linear(correlation(P, adv30, 4.01303), 2.6809))) * -1)；原目录：Alpha101_091；追踪：PF00091；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
