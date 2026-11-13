"""WorldQuant Alpha101

公式：((rank(Sign(delta(IndNeutralize(((O * 0.868128) + (H * (1 - 0.868128))), SW2), 4.04545)))^Ts_Rank(correlation(H, adv10, 5.11456), 5.53756)) * -1)；原目录：Alpha101_080；追踪：PF00080；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'industry_sw_2': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_2'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'alpha101_080_18d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '^', ('call', 'rank', [('call', 'sign', [('call', 'delta', [('call', 'indneutralize', [('bin', '+', ('bin', '*', ('var', 'O'), ('num', 0.868128)), ('bin', '*', ('var', 'H'), ('bin', '-', ('num', 1.0), ('num', 0.868128)))), ('var', 'SW2')]), ('num', 4.04545)])])]), ('call', 'ts_rank', [('call', 'correlation', [('var', 'H'), ('var', 'adv10'), ('num', 5.11456)]), ('num', 5.53756)])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_080_18d', {})
class Factor_alpha101_080_18d(PublicFactor):
    name = 'alpha101_080_18d'
    description = '((rank(Sign(delta(IndNeutralize(((O * 0.868128) + (H * (1 - 0.868128))), SW2), 4.04545)))^Ts_Rank(correlation(H, adv10, 5.11456), 5.53756)) * -1)；原目录：Alpha101_080；追踪：PF00080；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
