"""WorldQuant Alpha101

公式：(rank(correlation(delay((O - C), 1), C, 200)) + rank((O - C)))；原目录：Alpha101_037；追踪：PF00037；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'alpha101_037_201d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '+', ('call', 'rank', [('call', 'correlation', [('call', 'delay', [('bin', '-', ('var', 'O'), ('var', 'C')), ('num', 1.0)]), ('var', 'C'), ('num', 200.0)])]), ('call', 'rank', [('bin', '-', ('var', 'O'), ('var', 'C'))]))}

@register_factor
@fixed_factor('alpha101_037_201d', {})
class Factor_alpha101_037_201d(PublicFactor):
    name = 'alpha101_037_201d'
    description = '(rank(correlation(delay((O - C), 1), C, 200)) + rank((O - C)))；原目录：Alpha101_037；追踪：PF00037；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
