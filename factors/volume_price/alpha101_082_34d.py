"""WorldQuant Alpha101

公式：(min(rank(decay_linear(delta(O, 1.46063), 14.8717)), Ts_Rank(decay_linear(correlation(IndNeutralize(V, SW1), ((O * 0.634196) + (O * (1 - 0.634196))), 17.4842), 6.92131), 13.4283)) * -1)；原目录：Alpha101_082；追踪：PF00082；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_082_34d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('call', 'min', [('call', 'rank', [('call', 'decay_linear', [('call', 'delta', [('var', 'O'), ('num', 1.46063)]), ('num', 14.8717)])]), ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'correlation', [('call', 'indneutralize', [('var', 'V'), ('var', 'SW1')]), ('bin', '+', ('bin', '*', ('var', 'O'), ('num', 0.634196)), ('bin', '*', ('var', 'O'), ('bin', '-', ('num', 1.0), ('num', 0.634196)))), ('num', 17.4842)]), ('num', 6.92131)]), ('num', 13.4283)])]), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_082_34d', {})
class Factor_alpha101_082_34d(PublicFactor):
    name = 'alpha101_082_34d'
    description = '(min(rank(decay_linear(delta(O, 1.46063), 14.8717)), Ts_Rank(decay_linear(correlation(IndNeutralize(V, SW1), ((O * 0.634196) + (O * (1 - 0.634196))), 17.4842), 6.92131), 13.4283)) * -1)；原目录：Alpha101_082；追踪：PF00082；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
