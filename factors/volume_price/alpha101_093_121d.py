"""WorldQuant Alpha101

公式：(Ts_Rank(decay_linear(correlation(IndNeutralize(P, SW2), adv81, 17.4193), 19.848), 7.54455) / rank(decay_linear(delta(((C * 0.524434) + (P * (1 - 0.524434))), 2.77377), 16.2664)))；原目录：Alpha101_093；追踪：PF00093；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_093_121d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '/', ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'correlation', [('call', 'indneutralize', [('var', 'P'), ('var', 'SW2')]), ('var', 'adv81'), ('num', 17.4193)]), ('num', 19.848)]), ('num', 7.54455)]), ('call', 'rank', [('call', 'decay_linear', [('call', 'delta', [('bin', '+', ('bin', '*', ('var', 'C'), ('num', 0.524434)), ('bin', '*', ('var', 'P'), ('bin', '-', ('num', 1.0), ('num', 0.524434)))), ('num', 2.77377)]), ('num', 16.2664)])]))}

@register_factor
@fixed_factor('alpha101_093_121d', {})
class Factor_alpha101_093_121d(PublicFactor):
    name = 'alpha101_093_121d'
    description = '(Ts_Rank(decay_linear(correlation(IndNeutralize(P, SW2), adv81, 17.4193), 19.848), 7.54455) / rank(decay_linear(delta(((C * 0.524434) + (P * (1 - 0.524434))), 2.77377), 16.2664)))；原目录：Alpha101_093；追踪：PF00093；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
