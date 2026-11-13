"""WorldQuant Alpha101

公式：(-1 * ts_max(correlation(ts_rank(V, 5), ts_rank(H, 5), 5), 3))；原目录：Alpha101_026；追踪：PF00026；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha101_026_11d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'ts_max', [('call', 'correlation', [('call', 'ts_rank', [('var', 'V'), ('num', 5.0)]), ('call', 'ts_rank', [('var', 'H'), ('num', 5.0)]), ('num', 5.0)]), ('num', 3.0)]))}

@register_factor
@fixed_factor('alpha101_026_11d', {})
class Factor_alpha101_026_11d(PublicFactor):
    name = 'alpha101_026_11d'
    description = '(-1 * ts_max(correlation(ts_rank(V, 5), ts_rank(H, 5), 5), 3))；原目录：Alpha101_026；追踪：PF00026；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
