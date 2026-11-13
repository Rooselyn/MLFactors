"""WorldQuant Alpha101

公式：(0 - (1 * ((2 * scale(rank(((((C - L) - (H - C)) / (H - L)) * V)))) - scale(rank(ts_argmax(C, 10))))))；原目录：Alpha101_060；追踪：PF00060；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_060_10d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '-', ('num', 0.0), ('bin', '*', ('num', 1.0), ('bin', '-', ('bin', '*', ('num', 2.0), ('call', 'scale', [('call', 'rank', [('bin', '*', ('bin', '/', ('bin', '-', ('bin', '-', ('var', 'C'), ('var', 'L')), ('bin', '-', ('var', 'H'), ('var', 'C'))), ('bin', '-', ('var', 'H'), ('var', 'L'))), ('var', 'V'))])])), ('call', 'scale', [('call', 'rank', [('call', 'ts_argmax', [('var', 'C'), ('num', 10.0)])])]))))}

@register_factor
@fixed_factor('alpha101_060_10d', {})
class Factor_alpha101_060_10d(PublicFactor):
    name = 'alpha101_060_10d'
    description = '(0 - (1 * ((2 * scale(rank(((((C - L) - (H - C)) / (H - L)) * V)))) - scale(rank(ts_argmax(C, 10))))))；原目录：Alpha101_060；追踪：PF00060；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
