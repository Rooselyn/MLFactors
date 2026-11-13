"""WorldQuant Alpha101

公式：((Ts_Rank(correlation(rank(H), rank(adv15), 8.91644), 13.9333) < rank(delta(((C * 0.518371) + (L * (1 - 0.518371))), 1.06157))) * -1)；原目录：Alpha101_068；追踪：PF00068；[来源](https://arxiv.org/pdf/1601.00991)。
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
}
SPEC = {'name': 'alpha101_068_34d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '<', ('call', 'ts_rank', [('call', 'correlation', [('call', 'rank', [('var', 'H')]), ('call', 'rank', [('var', 'adv15')]), ('num', 8.91644)]), ('num', 13.9333)]), ('call', 'rank', [('call', 'delta', [('bin', '+', ('bin', '*', ('var', 'C'), ('num', 0.518371)), ('bin', '*', ('var', 'L'), ('bin', '-', ('num', 1.0), ('num', 0.518371)))), ('num', 1.06157)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_068_34d', {})
class Factor_alpha101_068_34d(PublicFactor):
    name = 'alpha101_068_34d'
    description = '((Ts_Rank(correlation(rank(H), rank(adv15), 8.91644), 13.9333) < rank(delta(((C * 0.518371) + (L * (1 - 0.518371))), 1.06157))) * -1)；原目录：Alpha101_068；追踪：PF00068；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
