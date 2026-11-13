"""WorldQuant Alpha101

公式：((C - O) / ((H - L) + .001))；原目录：Alpha101_101；追踪：PF00101；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_101_1d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '/', ('bin', '-', ('var', 'C'), ('var', 'O')), ('bin', '+', ('bin', '-', ('var', 'H'), ('var', 'L')), ('num', 0.001)))}

@register_factor
@fixed_factor('alpha101_101_1d', {})
class Factor_alpha101_101_1d(PublicFactor):
    name = 'alpha101_101_1d'
    description = '((C - O) / ((H - L) + .001))；原目录：Alpha101_101；追踪：PF00101；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
