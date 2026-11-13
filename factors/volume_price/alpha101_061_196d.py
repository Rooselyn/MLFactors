"""WorldQuant Alpha101

公式：(rank((P - ts_min(P, 16.1219))) < rank(correlation(P, adv180, 17.9282)))；原目录：Alpha101_061；追踪：PF00061；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_061_196d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '<', ('call', 'rank', [('bin', '-', ('var', 'P'), ('call', 'ts_min', [('var', 'P'), ('num', 16.1219)]))]), ('call', 'rank', [('call', 'correlation', [('var', 'P'), ('var', 'adv180'), ('num', 17.9282)])]))}

@register_factor
@fixed_factor('alpha101_061_196d', {})
class Factor_alpha101_061_196d(PublicFactor):
    name = 'alpha101_061_196d'
    description = '(rank((P - ts_min(P, 16.1219))) < rank(correlation(P, adv180, 17.9282)))；原目录：Alpha101_061；追踪：PF00061；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
