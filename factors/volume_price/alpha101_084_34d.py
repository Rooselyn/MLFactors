"""WorldQuant Alpha101

公式：SignedPower(Ts_Rank((P - ts_max(P, 15.3217)), 20.7127), delta(C, 4.96796))；原目录：Alpha101_084；追踪：PF00084；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_084_34d', 'engine': 'alpha', 'kind': 101, 'tree': ('call', 'signedpower', [('call', 'ts_rank', [('bin', '-', ('var', 'P'), ('call', 'ts_max', [('var', 'P'), ('num', 15.3217)])), ('num', 20.7127)]), ('call', 'delta', [('var', 'C'), ('num', 4.96796)])])}

@register_factor
@fixed_factor('alpha101_084_34d', {})
class Factor_alpha101_084_34d(PublicFactor):
    name = 'alpha101_084_34d'
    description = 'SignedPower(Ts_Rank((P - ts_max(P, 15.3217)), 20.7127), delta(C, 4.96796))；原目录：Alpha101_084；追踪：PF00084；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
