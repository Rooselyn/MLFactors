"""WorldQuant Alpha101

公式：((rank(delta(P, 1.29456))^Ts_Rank(correlation(IndNeutralize(C, SW2), adv50, 17.8256), 17.9171)) * -1)；原目录：Alpha101_070；追踪：PF00070；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_070_82d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '^', ('call', 'rank', [('call', 'delta', [('var', 'P'), ('num', 1.29456)])]), ('call', 'ts_rank', [('call', 'correlation', [('call', 'indneutralize', [('var', 'C'), ('var', 'SW2')]), ('var', 'adv50'), ('num', 17.8256)]), ('num', 17.9171)])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_070_82d', {})
class Factor_alpha101_070_82d(PublicFactor):
    name = 'alpha101_070_82d'
    description = '((rank(delta(P, 1.29456))^Ts_Rank(correlation(IndNeutralize(C, SW2), adv50, 17.8256), 17.9171)) * -1)；原目录：Alpha101_070；追踪：PF00070；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
