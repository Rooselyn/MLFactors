"""WorldQuant Alpha101

公式：((-1 * rank(Ts_Rank(C, 10))) * rank((C / O)))；原目录：Alpha101_038；追踪：PF00038；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'alpha101_038_10d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('call', 'ts_rank', [('var', 'C'), ('num', 10.0)])])), ('call', 'rank', [('bin', '/', ('var', 'C'), ('var', 'O'))]))}

@register_factor
@fixed_factor('alpha101_038_10d', {})
class Factor_alpha101_038_10d(PublicFactor):
    name = 'alpha101_038_10d'
    description = '((-1 * rank(Ts_Rank(C, 10))) * rank((C / O)))；原目录：Alpha101_038；追踪：PF00038；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
