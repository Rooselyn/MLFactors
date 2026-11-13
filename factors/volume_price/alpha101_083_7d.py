"""WorldQuant Alpha101

公式：((rank(delay(((H - L) / (sum(C, 5) / 5)), 2)) * rank(rank(V))) / (((H - L) / (sum(C, 5) / 5)) / (P - C)))；原目录：Alpha101_083；追踪：PF00083；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_114
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_083_7d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '/', ('bin', '*', ('call', 'rank', [('call', 'delay', [('bin', '/', ('bin', '-', ('var', 'H'), ('var', 'L')), ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 5.0)]), ('num', 5.0))), ('num', 2.0)])]), ('call', 'rank', [('call', 'rank', [('var', 'V')])])), ('bin', '/', ('bin', '/', ('bin', '-', ('var', 'H'), ('var', 'L')), ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 5.0)]), ('num', 5.0))), ('bin', '-', ('var', 'P'), ('var', 'C'))))}

@register_factor
@fixed_factor('alpha101_083_7d', {})
class Factor_alpha101_083_7d(PublicFactor):
    name = 'alpha101_083_7d'
    description = '((rank(delay(((H - L) / (sum(C, 5) / 5)), 2)) * rank(rank(V))) / (((H - L) / (sum(C, 5) / 5)) / (P - C)))；原目录：Alpha101_083；追踪：PF00083；[来源](https://arxiv.org/pdf/1601.00991)。；同定义来源别名：国泰君安 Alpha191:GTJA_Alpha191_114'
    INPUTS = INPUTS
    SPEC = SPEC
