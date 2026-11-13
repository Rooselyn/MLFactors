"""WorldQuant Alpha101

公式：((rank((P - ts_min(P, 11.5783)))^Ts_Rank(correlation(Ts_Rank(P, 19.6462), Ts_Rank(adv60, 4.02992), 18.0926), 2.70756)) * -1)；原目录：Alpha101_094；追踪：PF00094；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_094_81d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '^', ('call', 'rank', [('bin', '-', ('var', 'P'), ('call', 'ts_min', [('var', 'P'), ('num', 11.5783)]))]), ('call', 'ts_rank', [('call', 'correlation', [('call', 'ts_rank', [('var', 'P'), ('num', 19.6462)]), ('call', 'ts_rank', [('var', 'adv60'), ('num', 4.02992)]), ('num', 18.0926)]), ('num', 2.70756)])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_094_81d', {})
class Factor_alpha101_094_81d(PublicFactor):
    name = 'alpha101_094_81d'
    description = '((rank((P - ts_min(P, 11.5783)))^Ts_Rank(correlation(Ts_Rank(P, 19.6462), Ts_Rank(adv60, 4.02992), 18.0926), 2.70756)) * -1)；原目录：Alpha101_094；追踪：PF00094；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
