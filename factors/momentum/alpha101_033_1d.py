"""WorldQuant Alpha101

公式：rank((-1 * ((1 - (O / C))^1)))；原目录：Alpha101_033；追踪：PF00033；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'alpha101_033_1d', 'engine': 'alpha', 'kind': 101, 'tree': ('call', 'rank', [('bin', '*', ('unary', '-', ('num', 1.0)), ('bin', '^', ('bin', '-', ('num', 1.0), ('bin', '/', ('var', 'O'), ('var', 'C'))), ('num', 1.0)))])}

@register_factor
@fixed_factor('alpha101_033_1d', {})
class Factor_alpha101_033_1d(PublicFactor):
    name = 'alpha101_033_1d'
    description = 'rank((-1 * ((1 - (O / C))^1)))；原目录：Alpha101_033；追踪：PF00033；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
