"""WorldQuant Alpha101

公式：(-1 * Ts_Rank(decay_linear(correlation(IndNeutralize(((P * 0.728317) + (P * (1 - 0.728317))), SW2), V, 4.25197), 16.2289), 8.19648))；原目录：Alpha101_059；追踪：PF00059；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
    'industry_sw_2': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_2'),
}
SPEC = {'name': 'alpha101_059_26d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'correlation', [('call', 'indneutralize', [('bin', '+', ('bin', '*', ('var', 'P'), ('num', 0.728317)), ('bin', '*', ('var', 'P'), ('bin', '-', ('num', 1.0), ('num', 0.728317)))), ('var', 'SW2')]), ('var', 'V'), ('num', 4.25197)]), ('num', 16.2289)]), ('num', 8.19648)]))}

@register_factor
@fixed_factor('alpha101_059_26d', {})
class Factor_alpha101_059_26d(PublicFactor):
    name = 'alpha101_059_26d'
    description = '(-1 * Ts_Rank(decay_linear(correlation(IndNeutralize(((P * 0.728317) + (P * (1 - 0.728317))), SW2), V, 4.25197), 16.2289), 8.19648))；原目录：Alpha101_059；追踪：PF00059；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
