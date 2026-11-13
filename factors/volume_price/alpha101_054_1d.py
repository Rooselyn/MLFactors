"""WorldQuant Alpha101

公式：((-1 * ((L - C) * (O^5))) / ((L - H) * (C^5)))；原目录：Alpha101_054；追踪：PF00054；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_054_1d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '/', ('bin', '*', ('unary', '-', ('num', 1.0)), ('bin', '*', ('bin', '-', ('var', 'L'), ('var', 'C')), ('bin', '^', ('var', 'O'), ('num', 5.0)))), ('bin', '*', ('bin', '-', ('var', 'L'), ('var', 'H')), ('bin', '^', ('var', 'C'), ('num', 5.0))))}

@register_factor
@fixed_factor('alpha101_054_1d', {})
class Factor_alpha101_054_1d(PublicFactor):
    name = 'alpha101_054_1d'
    description = '((-1 * ((L - C) * (O^5))) / ((L - H) * (C^5)))；原目录：Alpha101_054；追踪：PF00054；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
