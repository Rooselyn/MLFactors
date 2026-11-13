"""WorldQuant Alpha101

公式：(((-1 * rank(ts_rank(C, 10))) * rank(delta(delta(C, 1), 1))) * rank(ts_rank((V / adv20), 5)))；原目录：Alpha101_017；追踪：PF00017；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_017_24d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '*', ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('call', 'ts_rank', [('var', 'C'), ('num', 10.0)])])), ('call', 'rank', [('call', 'delta', [('call', 'delta', [('var', 'C'), ('num', 1.0)]), ('num', 1.0)])])), ('call', 'rank', [('call', 'ts_rank', [('bin', '/', ('var', 'V'), ('var', 'adv20')), ('num', 5.0)])]))}

@register_factor
@fixed_factor('alpha101_017_24d', {})
class Factor_alpha101_017_24d(PublicFactor):
    name = 'alpha101_017_24d'
    description = '(((-1 * rank(ts_rank(C, 10))) * rank(delta(delta(C, 1), 1))) * rank(ts_rank((V / adv20), 5)))；原目录：Alpha101_017；追踪：PF00017；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
