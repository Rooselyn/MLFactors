"""WorldQuant Alpha101

公式：(-1 * correlation(rank(((C - ts_min(L, 12)) / (ts_max(H, 12) - ts_min(L, 12)))), rank(V), 6))；原目录：Alpha101_055；追踪：PF00055；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_055_17d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'correlation', [('call', 'rank', [('bin', '/', ('bin', '-', ('var', 'C'), ('call', 'ts_min', [('var', 'L'), ('num', 12.0)])), ('bin', '-', ('call', 'ts_max', [('var', 'H'), ('num', 12.0)]), ('call', 'ts_min', [('var', 'L'), ('num', 12.0)])))]), ('call', 'rank', [('var', 'V')]), ('num', 6.0)]))}

@register_factor
@fixed_factor('alpha101_055_17d', {})
class Factor_alpha101_055_17d(PublicFactor):
    name = 'alpha101_055_17d'
    description = '(-1 * correlation(rank(((C - ts_min(L, 12)) / (ts_max(H, 12) - ts_min(L, 12)))), rank(V), 6))；原目录：Alpha101_055；追踪：PF00055；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
