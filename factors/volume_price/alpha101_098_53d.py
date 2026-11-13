"""WorldQuant Alpha101

公式：(rank(decay_linear(correlation(P, sum(adv5, 26.4719), 4.58418), 7.18088)) - rank(decay_linear(Ts_Rank(Ts_ArgMin(correlation(rank(O), rank(adv15), 20.8187), 8.62571), 6.95668), 8.07206)))；原目录：Alpha101_098；追踪：PF00098；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_098_53d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '-', ('call', 'rank', [('call', 'decay_linear', [('call', 'correlation', [('var', 'P'), ('call', 'sum', [('var', 'adv5'), ('num', 26.4719)]), ('num', 4.58418)]), ('num', 7.18088)])]), ('call', 'rank', [('call', 'decay_linear', [('call', 'ts_rank', [('call', 'ts_argmin', [('call', 'correlation', [('call', 'rank', [('var', 'O')]), ('call', 'rank', [('var', 'adv15')]), ('num', 20.8187)]), ('num', 8.62571)]), ('num', 6.95668)]), ('num', 8.07206)])]))}

@register_factor
@fixed_factor('alpha101_098_53d', {})
class Factor_alpha101_098_53d(PublicFactor):
    name = 'alpha101_098_53d'
    description = '(rank(decay_linear(correlation(P, sum(adv5, 26.4719), 4.58418), 7.18088)) - rank(decay_linear(Ts_Rank(Ts_ArgMin(correlation(rank(O), rank(adv15), 20.8187), 8.62571), 6.95668), 8.07206)))；原目录：Alpha101_098；追踪：PF00098；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
