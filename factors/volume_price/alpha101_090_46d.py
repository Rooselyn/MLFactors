"""WorldQuant Alpha101

公式：((rank((C - ts_max(C, 4.66719)))^Ts_Rank(correlation(IndNeutralize(adv40, SW3), L, 5.38375), 3.21856)) * -1)；原目录：Alpha101_090；追踪：PF00090；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'industry_sw_3': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_3'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'alpha101_090_46d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '^', ('call', 'rank', [('bin', '-', ('var', 'C'), ('call', 'ts_max', [('var', 'C'), ('num', 4.66719)]))]), ('call', 'ts_rank', [('call', 'correlation', [('call', 'indneutralize', [('var', 'adv40'), ('var', 'SW3')]), ('var', 'L'), ('num', 5.38375)]), ('num', 3.21856)])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_090_46d', {})
class Factor_alpha101_090_46d(PublicFactor):
    name = 'alpha101_090_46d'
    description = '((rank((C - ts_max(C, 4.66719)))^Ts_Rank(correlation(IndNeutralize(adv40, SW3), L, 5.38375), 3.21856)) * -1)；原目录：Alpha101_090；追踪：PF00090；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
