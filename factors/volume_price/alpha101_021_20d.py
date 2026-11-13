"""WorldQuant Alpha101

公式：((((sum(C, 8) / 8) + stddev(C, 8)) < (sum(C, 2) / 2)) ? (-1 * 1) : (((sum(C, 2) / 2) < ((sum(C, 8) / 8) - stddev(C, 8))) ? 1 : (((1 < (V / adv20)) || ((V / adv20) == 1)) ? 1 : (-1 * 1))))；原目录：Alpha101_021；追踪：PF00021；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_021_20d', 'engine': 'alpha', 'kind': 101, 'tree': ('if', ('bin', '<', ('bin', '+', ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 8.0)]), ('num', 8.0)), ('call', 'stddev', [('var', 'C'), ('num', 8.0)])), ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 2.0)]), ('num', 2.0))), ('bin', '*', ('unary', '-', ('num', 1.0)), ('num', 1.0)), ('if', ('bin', '<', ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 2.0)]), ('num', 2.0)), ('bin', '-', ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 8.0)]), ('num', 8.0)), ('call', 'stddev', [('var', 'C'), ('num', 8.0)]))), ('num', 1.0), ('if', ('bin', '||', ('bin', '<', ('num', 1.0), ('bin', '/', ('var', 'V'), ('var', 'adv20'))), ('bin', '==', ('bin', '/', ('var', 'V'), ('var', 'adv20')), ('num', 1.0))), ('num', 1.0), ('bin', '*', ('unary', '-', ('num', 1.0)), ('num', 1.0)))))}

@register_factor
@fixed_factor('alpha101_021_20d', {})
class Factor_alpha101_021_20d(PublicFactor):
    name = 'alpha101_021_20d'
    description = '((((sum(C, 8) / 8) + stddev(C, 8)) < (sum(C, 2) / 2)) ? (-1 * 1) : (((sum(C, 2) / 2) < ((sum(C, 8) / 8) - stddev(C, 8))) ? 1 : (((1 < (V / adv20)) || ((V / adv20) == 1)) ? 1 : (-1 * 1))))；原目录：Alpha101_021；追踪：PF00021；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
