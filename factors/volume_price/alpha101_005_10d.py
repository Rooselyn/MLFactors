"""WorldQuant Alpha101

公式：(rank((O - (sum(P, 10) / 10))) * (-1 * abs(rank((C - P)))))；原目录：Alpha101_005；追踪：PF00005；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_005_10d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('call', 'rank', [('bin', '-', ('var', 'O'), ('bin', '/', ('call', 'sum', [('var', 'P'), ('num', 10.0)]), ('num', 10.0)))]), ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'abs', [('call', 'rank', [('bin', '-', ('var', 'C'), ('var', 'P'))])])))}

@register_factor
@fixed_factor('alpha101_005_10d', {})
class Factor_alpha101_005_10d(PublicFactor):
    name = 'alpha101_005_10d'
    description = '(rank((O - (sum(P, 10) / 10))) * (-1 * abs(rank((C - P)))))；原目录：Alpha101_005；追踪：PF00005；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
