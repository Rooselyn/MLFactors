"""WorldQuant Alpha101

公式：(-1 * delta((((C - L) - (H - C)) / (C - L)), 9))；原目录：Alpha101_053；追踪：PF00053；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'alpha101_053_10d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'delta', [('bin', '/', ('bin', '-', ('bin', '-', ('var', 'C'), ('var', 'L')), ('bin', '-', ('var', 'H'), ('var', 'C'))), ('bin', '-', ('var', 'C'), ('var', 'L'))), ('num', 9.0)]))}

@register_factor
@fixed_factor('alpha101_053_10d', {})
class Factor_alpha101_053_10d(PublicFactor):
    name = 'alpha101_053_10d'
    description = '(-1 * delta((((C - L) - (H - C)) / (C - L)), 9))；原目录：Alpha101_053；追踪：PF00053；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
