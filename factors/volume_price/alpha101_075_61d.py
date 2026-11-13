"""WorldQuant Alpha101

公式：(rank(correlation(P, V, 4.24304)) < rank(correlation(rank(L), rank(adv50), 12.4413)))；原目录：Alpha101_075；追踪：PF00075；[来源](https://arxiv.org/pdf/1601.00991)。
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
}
SPEC = {'name': 'alpha101_075_61d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '<', ('call', 'rank', [('call', 'correlation', [('var', 'P'), ('var', 'V'), ('num', 4.24304)])]), ('call', 'rank', [('call', 'correlation', [('call', 'rank', [('var', 'L')]), ('call', 'rank', [('var', 'adv50')]), ('num', 12.4413)])]))}

@register_factor
@fixed_factor('alpha101_075_61d', {})
class Factor_alpha101_075_61d(PublicFactor):
    name = 'alpha101_075_61d'
    description = '(rank(correlation(P, V, 4.24304)) < rank(correlation(rank(L), rank(adv50), 12.4413)))；原目录：Alpha101_075；追踪：PF00075；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
