"""WorldQuant Alpha101

公式：(ts_rank((V / adv20), 20) * ts_rank((-1 * delta(C, 7)), 8))；原目录：Alpha101_043；追踪：PF00043；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_043_39d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('call', 'ts_rank', [('bin', '/', ('var', 'V'), ('var', 'adv20')), ('num', 20.0)]), ('call', 'ts_rank', [('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'delta', [('var', 'C'), ('num', 7.0)])), ('num', 8.0)]))}

@register_factor
@fixed_factor('alpha101_043_39d', {})
class Factor_alpha101_043_39d(PublicFactor):
    name = 'alpha101_043_39d'
    description = '(ts_rank((V / adv20), 20) * ts_rank((-1 * delta(C, 7)), 8))；原目录：Alpha101_043；追踪：PF00043；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
