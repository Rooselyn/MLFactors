"""WorldQuant Alpha101

公式：(-1 * (delta(correlation(H, V, 5), 5) * rank(stddev(C, 20))))；原目录：Alpha101_022；追踪：PF00022；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_022_20d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('bin', '*', ('call', 'delta', [('call', 'correlation', [('var', 'H'), ('var', 'V'), ('num', 5.0)]), ('num', 5.0)]), ('call', 'rank', [('call', 'stddev', [('var', 'C'), ('num', 20.0)])])))}

@register_factor
@fixed_factor('alpha101_022_20d', {})
class Factor_alpha101_022_20d(PublicFactor):
    name = 'alpha101_022_20d'
    description = '(-1 * (delta(correlation(H, V, 5), 5) * rank(stddev(C, 20))))；原目录：Alpha101_022；追踪：PF00022；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
