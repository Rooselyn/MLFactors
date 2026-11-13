"""WorldQuant Alpha101

公式：((adv20 < V) ? ((-1 * ts_rank(abs(delta(C, 7)), 60)) * sign(delta(C, 7))) : (-1 * 1))；原目录：Alpha101_007；追踪：PF00007；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'alpha101_007_67d', 'engine': 'alpha', 'kind': 101, 'tree': ('if', ('bin', '<', ('var', 'adv20'), ('var', 'V')), ('bin', '*', ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'ts_rank', [('call', 'abs', [('call', 'delta', [('var', 'C'), ('num', 7.0)])]), ('num', 60.0)])), ('call', 'sign', [('call', 'delta', [('var', 'C'), ('num', 7.0)])])), ('bin', '*', ('unary', '-', ('num', 1.0)), ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_007_67d', {})
class Factor_alpha101_007_67d(PublicFactor):
    name = 'alpha101_007_67d'
    description = '((adv20 < V) ? ((-1 * ts_rank(abs(delta(C, 7)), 60)) * sign(delta(C, 7))) : (-1 * 1))；原目录：Alpha101_007；追踪：PF00007；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
