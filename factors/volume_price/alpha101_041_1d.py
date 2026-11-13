"""WorldQuant Alpha101

公式：(((H * L)^0.5) - P)；原目录：Alpha101_041；追踪：PF00041；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_013
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_041_1d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '-', ('bin', '^', ('bin', '*', ('var', 'H'), ('var', 'L')), ('num', 0.5)), ('var', 'P'))}

@register_factor
@fixed_factor('alpha101_041_1d', {})
class Factor_alpha101_041_1d(PublicFactor):
    name = 'alpha101_041_1d'
    description = '(((H * L)^0.5) - P)；原目录：Alpha101_041；追踪：PF00041；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_013'
    INPUTS = INPUTS
    SPEC = SPEC
