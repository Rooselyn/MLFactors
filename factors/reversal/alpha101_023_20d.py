"""WorldQuant Alpha101

公式：(((sum(H, 20) / 20) < H) ? (-1 * delta(H, 2)) : 0)；原目录：Alpha101_023；追踪：PF00023；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_038
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
}
SPEC = {'name': 'alpha101_023_20d', 'engine': 'alpha', 'kind': 101, 'tree': ('if', ('bin', '<', ('bin', '/', ('call', 'sum', [('var', 'H'), ('num', 20.0)]), ('num', 20.0)), ('var', 'H')), ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'delta', [('var', 'H'), ('num', 2.0)])), ('num', 0.0))}

@register_factor
@fixed_factor('alpha101_023_20d', {})
class Factor_alpha101_023_20d(PublicFactor):
    name = 'alpha101_023_20d'
    description = '(((sum(H, 20) / 20) < H) ? (-1 * delta(H, 2)) : 0)；原目录：Alpha101_023；追踪：PF00023；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_038'
    INPUTS = INPUTS
    SPEC = SPEC
