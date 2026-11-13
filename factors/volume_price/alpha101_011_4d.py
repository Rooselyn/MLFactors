"""WorldQuant Alpha101

公式：((rank(ts_max((P - C), 3)) + rank(ts_min((P - C), 3))) * rank(delta(V, 3)))；原目录：Alpha101_011；追踪：PF00011；[来源](https://arxiv.org/pdf/1601.00991)。
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
}
SPEC = {'name': 'alpha101_011_4d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '+', ('call', 'rank', [('call', 'ts_max', [('bin', '-', ('var', 'P'), ('var', 'C')), ('num', 3.0)])]), ('call', 'rank', [('call', 'ts_min', [('bin', '-', ('var', 'P'), ('var', 'C')), ('num', 3.0)])])), ('call', 'rank', [('call', 'delta', [('var', 'V'), ('num', 3.0)])]))}

@register_factor
@fixed_factor('alpha101_011_4d', {})
class Factor_alpha101_011_4d(PublicFactor):
    name = 'alpha101_011_4d'
    description = '((rank(ts_max((P - C), 3)) + rank(ts_min((P - C), 3))) * rank(delta(V, 3)))；原目录：Alpha101_011；追踪：PF00011；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
