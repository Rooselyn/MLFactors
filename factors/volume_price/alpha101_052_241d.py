"""WorldQuant Alpha101

公式：((((-1 * ts_min(L, 5)) + delay(ts_min(L, 5), 5)) * rank(((sum(R, 240) - sum(R, 20)) / 220))) * ts_rank(V, 5))；原目录：Alpha101_052；追踪：PF00052；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_052_241d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '*', ('bin', '+', ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'ts_min', [('var', 'L'), ('num', 5.0)])), ('call', 'delay', [('call', 'ts_min', [('var', 'L'), ('num', 5.0)]), ('num', 5.0)])), ('call', 'rank', [('bin', '/', ('bin', '-', ('call', 'sum', [('var', 'R'), ('num', 240.0)]), ('call', 'sum', [('var', 'R'), ('num', 20.0)])), ('num', 220.0))])), ('call', 'ts_rank', [('var', 'V'), ('num', 5.0)]))}

@register_factor
@fixed_factor('alpha101_052_241d', {})
class Factor_alpha101_052_241d(PublicFactor):
    name = 'alpha101_052_241d'
    description = '((((-1 * ts_min(L, 5)) + delay(ts_min(L, 5), 5)) * rank(((sum(R, 240) - sum(R, 20)) / 220))) * ts_rank(V, 5))；原目录：Alpha101_052；追踪：PF00052；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
