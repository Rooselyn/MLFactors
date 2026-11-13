"""WorldQuant Alpha101

公式：(Ts_Rank(decay_linear(correlation(((L * 0.967285) + (L * (1 - 0.967285))), adv10, 6.94279), 5.51607), 3.79744) - Ts_Rank(decay_linear(delta(IndNeutralize(P, SW2), 3.48158), 10.1466), 15.3012))；原目录：Alpha101_089；追踪：PF00089；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_089_27d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '-', ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'correlation', [('bin', '+', ('bin', '*', ('var', 'L'), ('num', 0.967285)), ('bin', '*', ('var', 'L'), ('bin', '-', ('num', 1.0), ('num', 0.967285)))), ('var', 'adv10'), ('num', 6.94279)]), ('num', 5.51607)]), ('num', 3.79744)]), ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'delta', [('call', 'indneutralize', [('var', 'P'), ('var', 'SW2')]), ('num', 3.48158)]), ('num', 10.1466)]), ('num', 15.3012)]))}

@register_factor
@fixed_factor('alpha101_089_27d', {})
class Factor_alpha101_089_27d(PublicFactor):
    name = 'alpha101_089_27d'
    description = '(Ts_Rank(decay_linear(correlation(((L * 0.967285) + (L * (1 - 0.967285))), adv10, 6.94279), 5.51607), 3.79744) - Ts_Rank(decay_linear(delta(IndNeutralize(P, SW2), 3.48158), 10.1466), 15.3012))；原目录：Alpha101_089；追踪：PF00089；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
