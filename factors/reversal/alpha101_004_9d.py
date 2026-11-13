"""WorldQuant Alpha101

公式：(-1 * Ts_Rank(rank(L), 9))；原目录：Alpha101_004；追踪：PF00004；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'alpha101_004_9d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'ts_rank', [('call', 'rank', [('var', 'L')]), ('num', 9.0)]))}

@register_factor
@fixed_factor('alpha101_004_9d', {})
class Factor_alpha101_004_9d(PublicFactor):
    name = 'alpha101_004_9d'
    description = '(-1 * Ts_Rank(rank(L), 9))；原目录：Alpha101_004；追踪：PF00004；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
