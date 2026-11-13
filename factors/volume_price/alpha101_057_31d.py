"""WorldQuant Alpha101

公式：(0 - (1 * ((C - P) / decay_linear(rank(ts_argmax(C, 30)), 2))))；原目录：Alpha101_057；追踪：PF00057；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_057_31d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '-', ('num', 0.0), ('bin', '*', ('num', 1.0), ('bin', '/', ('bin', '-', ('var', 'C'), ('var', 'P')), ('call', 'decay_linear', [('call', 'rank', [('call', 'ts_argmax', [('var', 'C'), ('num', 30.0)])]), ('num', 2.0)]))))}

@register_factor
@fixed_factor('alpha101_057_31d', {})
class Factor_alpha101_057_31d(PublicFactor):
    name = 'alpha101_057_31d'
    description = '(0 - (1 * ((C - P) / decay_linear(rank(ts_argmax(C, 30)), 2))))；原目录：Alpha101_057；追踪：PF00057；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
