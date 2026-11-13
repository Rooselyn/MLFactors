"""WorldQuant Alpha101

公式：(rank((O - ts_min(O, 12.4105))) < Ts_Rank((rank(correlation(sum(((H + L) / 2), 19.1351), sum(adv40, 19.1351), 12.8742))^5), 11.7584))；原目录：Alpha101_095；追踪：PF00095；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'alpha101_095_79d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '<', ('call', 'rank', [('bin', '-', ('var', 'O'), ('call', 'ts_min', [('var', 'O'), ('num', 12.4105)]))]), ('call', 'ts_rank', [('bin', '^', ('call', 'rank', [('call', 'correlation', [('call', 'sum', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('num', 19.1351)]), ('call', 'sum', [('var', 'adv40'), ('num', 19.1351)]), ('num', 12.8742)])]), ('num', 5.0)), ('num', 11.7584)]))}

@register_factor
@fixed_factor('alpha101_095_79d', {})
class Factor_alpha101_095_79d(PublicFactor):
    name = 'alpha101_095_79d'
    description = '(rank((O - ts_min(O, 12.4105))) < Ts_Rank((rank(correlation(sum(((H + L) / 2), 19.1351), sum(adv40, 19.1351), 12.8742))^5), 11.7584))；原目录：Alpha101_095；追踪：PF00095；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
