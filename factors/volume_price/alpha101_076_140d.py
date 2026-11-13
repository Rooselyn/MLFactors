"""WorldQuant Alpha101

公式：(max(rank(decay_linear(delta(P, 1.24383), 11.8259)), Ts_Rank(decay_linear(Ts_Rank(correlation(IndNeutralize(L, SW1), adv81, 8.14941), 19.569), 17.1543), 19.383)) * -1)；原目录：Alpha101_076；追踪：PF00076；[来源](https://arxiv.org/pdf/1601.00991)。
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
    'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1'),
}
SPEC = {'name': 'alpha101_076_140d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('call', 'max', [('call', 'rank', [('call', 'decay_linear', [('call', 'delta', [('var', 'P'), ('num', 1.24383)]), ('num', 11.8259)])]), ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'ts_rank', [('call', 'correlation', [('call', 'indneutralize', [('var', 'L'), ('var', 'SW1')]), ('var', 'adv81'), ('num', 8.14941)]), ('num', 19.569)]), ('num', 17.1543)]), ('num', 19.383)])]), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_076_140d', {})
class Factor_alpha101_076_140d(PublicFactor):
    name = 'alpha101_076_140d'
    description = '(max(rank(decay_linear(delta(P, 1.24383), 11.8259)), Ts_Rank(decay_linear(Ts_Rank(correlation(IndNeutralize(L, SW1), adv81, 8.14941), 19.569), 17.1543), 19.383)) * -1)；原目录：Alpha101_076；追踪：PF00076；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
