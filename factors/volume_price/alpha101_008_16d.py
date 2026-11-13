"""WorldQuant Alpha101

公式：(-1 * rank(((sum(O, 5) * sum(R, 5)) - delay((sum(O, 5) * sum(R, 5)), 10))))；原目录：Alpha101_008；追踪：PF00008；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_037
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha101_008_16d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('bin', '-', ('bin', '*', ('call', 'sum', [('var', 'O'), ('num', 5.0)]), ('call', 'sum', [('var', 'R'), ('num', 5.0)])), ('call', 'delay', [('bin', '*', ('call', 'sum', [('var', 'O'), ('num', 5.0)]), ('call', 'sum', [('var', 'R'), ('num', 5.0)])), ('num', 10.0)]))]))}

@register_factor
@fixed_factor('alpha101_008_16d', {})
class Factor_alpha101_008_16d(PublicFactor):
    name = 'alpha101_008_16d'
    description = '(-1 * rank(((sum(O, 5) * sum(R, 5)) - delay((sum(O, 5) * sum(R, 5)), 10))))；原目录：Alpha101_008；追踪：PF00008；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_037'
    INPUTS = INPUTS
    SPEC = SPEC
