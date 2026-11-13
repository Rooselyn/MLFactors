"""WorldQuant Alpha101

公式：((rank(decay_linear(delta(IndNeutralize(C, SW2), 2.25164), 8.22237)) - rank(decay_linear(correlation(((P * 0.318108) + (O * (1 - 0.318108))), sum(adv180, 37.2467), 13.557), 12.2883))) * -1)；原目录：Alpha101_063；追踪：PF00063；[来源](https://arxiv.org/pdf/1601.00991)。
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
    'industry_sw_2': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_2'),
}
SPEC = {'name': 'alpha101_063_239d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '-', ('call', 'rank', [('call', 'decay_linear', [('call', 'delta', [('call', 'indneutralize', [('var', 'C'), ('var', 'SW2')]), ('num', 2.25164)]), ('num', 8.22237)])]), ('call', 'rank', [('call', 'decay_linear', [('call', 'correlation', [('bin', '+', ('bin', '*', ('var', 'P'), ('num', 0.318108)), ('bin', '*', ('var', 'O'), ('bin', '-', ('num', 1.0), ('num', 0.318108)))), ('call', 'sum', [('var', 'adv180'), ('num', 37.2467)]), ('num', 13.557)]), ('num', 12.2883)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_063_239d', {})
class Factor_alpha101_063_239d(PublicFactor):
    name = 'alpha101_063_239d'
    description = '((rank(decay_linear(delta(IndNeutralize(C, SW2), 2.25164), 8.22237)) - rank(decay_linear(correlation(((P * 0.318108) + (O * (1 - 0.318108))), sum(adv180, 37.2467), 13.557), 12.2883))) * -1)；原目录：Alpha101_063；追踪：PF00063；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
