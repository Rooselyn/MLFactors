"""WorldQuant Alpha101

公式：(rank(decay_linear(correlation(((H + L) / 2), adv40, 8.93345), 10.1519)) / rank(decay_linear(correlation(Ts_Rank(P, 3.72469), Ts_Rank(V, 18.5188), 6.86671), 2.95011)))；原目录：Alpha101_072；追踪：PF00072；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_072_56d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '/', ('call', 'rank', [('call', 'decay_linear', [('call', 'correlation', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('var', 'adv40'), ('num', 8.93345)]), ('num', 10.1519)])]), ('call', 'rank', [('call', 'decay_linear', [('call', 'correlation', [('call', 'ts_rank', [('var', 'P'), ('num', 3.72469)]), ('call', 'ts_rank', [('var', 'V'), ('num', 18.5188)]), ('num', 6.86671)]), ('num', 2.95011)])]))}

@register_factor
@fixed_factor('alpha101_072_56d', {})
class Factor_alpha101_072_56d(PublicFactor):
    name = 'alpha101_072_56d'
    description = '(rank(decay_linear(correlation(((H + L) / 2), adv40, 8.93345), 10.1519)) / rank(decay_linear(correlation(Ts_Rank(P, 3.72469), Ts_Rank(V, 18.5188), 6.86671), 2.95011)))；原目录：Alpha101_072；追踪：PF00072；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
