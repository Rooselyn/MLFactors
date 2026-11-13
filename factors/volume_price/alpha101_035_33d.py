"""WorldQuant Alpha101

公式：((Ts_Rank(V, 32) * (1 - Ts_Rank(((C + H) - L), 16))) * (1 - Ts_Rank(R, 32)))；原目录：Alpha101_035；追踪：PF00035；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_035_33d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '*', ('call', 'ts_rank', [('var', 'V'), ('num', 32.0)]), ('bin', '-', ('num', 1.0), ('call', 'ts_rank', [('bin', '-', ('bin', '+', ('var', 'C'), ('var', 'H')), ('var', 'L')), ('num', 16.0)]))), ('bin', '-', ('num', 1.0), ('call', 'ts_rank', [('var', 'R'), ('num', 32.0)])))}

@register_factor
@fixed_factor('alpha101_035_33d', {})
class Factor_alpha101_035_33d(PublicFactor):
    name = 'alpha101_035_33d'
    description = '((Ts_Rank(V, 32) * (1 - Ts_Rank(((C + H) - L), 16))) * (1 - Ts_Rank(R, 32)))；原目录：Alpha101_035；追踪：PF00035；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
