"""WorldQuant Alpha101

公式：(rank((P - C)) / rank((P + C)))；原目录：Alpha101_042；追踪：PF00042；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_120
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_042_1d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '/', ('call', 'rank', [('bin', '-', ('var', 'P'), ('var', 'C'))]), ('call', 'rank', [('bin', '+', ('var', 'P'), ('var', 'C'))]))}

@register_factor
@fixed_factor('alpha101_042_1d', {})
class Factor_alpha101_042_1d(PublicFactor):
    name = 'alpha101_042_1d'
    description = '(rank((P - C)) / rank((P + C)))；原目录：Alpha101_042；追踪：PF00042；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_120'
    INPUTS = INPUTS
    SPEC = SPEC
