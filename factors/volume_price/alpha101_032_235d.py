"""WorldQuant Alpha101

公式：(scale(((sum(C, 7) / 7) - C)) + (20 * scale(correlation(P, delay(C, 5), 230))))；原目录：Alpha101_032；追踪：PF00032；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_032_235d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '+', ('call', 'scale', [('bin', '-', ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 7.0)]), ('num', 7.0)), ('var', 'C'))]), ('bin', '*', ('num', 20.0), ('call', 'scale', [('call', 'correlation', [('var', 'P'), ('call', 'delay', [('var', 'C'), ('num', 5.0)]), ('num', 230.0)])])))}

@register_factor
@fixed_factor('alpha101_032_235d', {})
class Factor_alpha101_032_235d(PublicFactor):
    name = 'alpha101_032_235d'
    description = '(scale(((sum(C, 7) / 7) - C)) + (20 * scale(correlation(P, delay(C, 5), 230))))；原目录：Alpha101_032；追踪：PF00032；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
