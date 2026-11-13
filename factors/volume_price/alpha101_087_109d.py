"""WorldQuant Alpha101

公式：(max(rank(decay_linear(delta(((C * 0.369701) + (P * (1 - 0.369701))), 1.91233), 2.65461)), Ts_Rank(decay_linear(abs(correlation(IndNeutralize(adv81, SW2), C, 13.4132)), 4.89768), 14.4535)) * -1)；原目录：Alpha101_087；追踪：PF00087；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_087_109d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('call', 'max', [('call', 'rank', [('call', 'decay_linear', [('call', 'delta', [('bin', '+', ('bin', '*', ('var', 'C'), ('num', 0.369701)), ('bin', '*', ('var', 'P'), ('bin', '-', ('num', 1.0), ('num', 0.369701)))), ('num', 1.91233)]), ('num', 2.65461)])]), ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'abs', [('call', 'correlation', [('call', 'indneutralize', [('var', 'adv81'), ('var', 'SW2')]), ('var', 'C'), ('num', 13.4132)])]), ('num', 4.89768)]), ('num', 14.4535)])]), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_087_109d', {})
class Factor_alpha101_087_109d(PublicFactor):
    name = 'alpha101_087_109d'
    description = '(max(rank(decay_linear(delta(((C * 0.369701) + (P * (1 - 0.369701))), 1.91233), 2.65461)), Ts_Rank(decay_linear(abs(correlation(IndNeutralize(adv81, SW2), C, 13.4132)), 4.89768), 14.4535)) * -1)；原目录：Alpha101_087；追踪：PF00087；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
