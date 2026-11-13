"""WorldQuant Alpha101

公式：(((-1 * rank((O - delay(H, 1)))) * rank((O - delay(C, 1)))) * rank((O - delay(L, 1))))；原目录：Alpha101_020；追踪：PF00020；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_107
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'alpha101_020_2d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '*', ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('bin', '-', ('var', 'O'), ('call', 'delay', [('var', 'H'), ('num', 1.0)]))])), ('call', 'rank', [('bin', '-', ('var', 'O'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))])), ('call', 'rank', [('bin', '-', ('var', 'O'), ('call', 'delay', [('var', 'L'), ('num', 1.0)]))]))}

@register_factor
@fixed_factor('alpha101_020_2d', {})
class Factor_alpha101_020_2d(PublicFactor):
    name = 'alpha101_020_2d'
    description = '(((-1 * rank((O - delay(H, 1)))) * rank((O - delay(C, 1)))) * rank((O - delay(L, 1))))；原目录：Alpha101_020；追踪：PF00020；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_107'
    INPUTS = INPUTS
    SPEC = SPEC
