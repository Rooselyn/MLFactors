"""WorldQuant Alpha101

公式：((0.25 < (((delay(C, 20) - delay(C, 10)) / 10) - ((delay(C, 10) - C) / 10))) ? (-1 * 1) : (((((delay(C, 20) - delay(C, 10)) / 10) - ((delay(C, 10) - C) / 10)) < 0) ? 1 : ((-1 * 1) * (C - delay(C, 1)))))；原目录：Alpha101_046；追踪：PF00046；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_086
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha101_046_21d', 'engine': 'alpha', 'kind': 101, 'tree': ('if', ('bin', '<', ('num', 0.25), ('bin', '-', ('bin', '/', ('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 20.0)]), ('call', 'delay', [('var', 'C'), ('num', 10.0)])), ('num', 10.0)), ('bin', '/', ('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 10.0)]), ('var', 'C')), ('num', 10.0)))), ('bin', '*', ('unary', '-', ('num', 1.0)), ('num', 1.0)), ('if', ('bin', '<', ('bin', '-', ('bin', '/', ('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 20.0)]), ('call', 'delay', [('var', 'C'), ('num', 10.0)])), ('num', 10.0)), ('bin', '/', ('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 10.0)]), ('var', 'C')), ('num', 10.0))), ('num', 0.0)), ('num', 1.0), ('bin', '*', ('bin', '*', ('unary', '-', ('num', 1.0)), ('num', 1.0)), ('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 1.0)])))))}

@register_factor
@fixed_factor('alpha101_046_21d', {})
class Factor_alpha101_046_21d(PublicFactor):
    name = 'alpha101_046_21d'
    description = '((0.25 < (((delay(C, 20) - delay(C, 10)) / 10) - ((delay(C, 10) - C) / 10))) ? (-1 * 1) : (((((delay(C, 20) - delay(C, 10)) / 10) - ((delay(C, 10) - C) / 10)) < 0) ? 1 : ((-1 * 1) * (C - delay(C, 1)))))；原目录：Alpha101_046；追踪：PF00046；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_086'
    INPUTS = INPUTS
    SPEC = SPEC
