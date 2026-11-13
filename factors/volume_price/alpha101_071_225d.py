"""WorldQuant Alpha101

公式：max(Ts_Rank(decay_linear(correlation(Ts_Rank(C, 3.43976), Ts_Rank(adv180, 12.0647), 18.0175), 4.20501), 15.6948), Ts_Rank(decay_linear((rank(((L + O) - (P + P)))^2), 16.4662), 4.4388))；原目录：Alpha101_071；追踪：PF00071；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_071_225d', 'engine': 'alpha', 'kind': 101, 'tree': ('call', 'max', [('call', 'ts_rank', [('call', 'decay_linear', [('call', 'correlation', [('call', 'ts_rank', [('var', 'C'), ('num', 3.43976)]), ('call', 'ts_rank', [('var', 'adv180'), ('num', 12.0647)]), ('num', 18.0175)]), ('num', 4.20501)]), ('num', 15.6948)]), ('call', 'ts_rank', [('call', 'decay_linear', [('bin', '^', ('call', 'rank', [('bin', '-', ('bin', '+', ('var', 'L'), ('var', 'O')), ('bin', '+', ('var', 'P'), ('var', 'P')))]), ('num', 2.0)), ('num', 16.4662)]), ('num', 4.4388)])])}

@register_factor
@fixed_factor('alpha101_071_225d', {})
class Factor_alpha101_071_225d(PublicFactor):
    name = 'alpha101_071_225d'
    description = 'max(Ts_Rank(decay_linear(correlation(Ts_Rank(C, 3.43976), Ts_Rank(adv180, 12.0647), 18.0175), 4.20501), 15.6948), Ts_Rank(decay_linear((rank(((L + O) - (P + P)))^2), 16.4662), 4.4388))；原目录：Alpha101_071；追踪：PF00071；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
