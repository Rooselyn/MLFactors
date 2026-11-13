"""WorldQuant Alpha101

公式：min(rank(decay_linear(((rank(O) + rank(L)) - (rank(H) + rank(C))), 8.06882)), Ts_Rank(decay_linear(correlation(Ts_Rank(C, 8.44728), Ts_Rank(adv60, 20.6966), 8.01266), 6.65053), 2.61957))；原目录：Alpha101_088；追踪：PF00088；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'alpha101_088_92d', 'engine': 'alpha', 'kind': 101, 'tree': ('call', 'min', [('call', 'rank', [('call', 'decay_linear', [('bin', '-', ('bin', '+', ('call', 'rank', [('var', 'O')]), ('call', 'rank', [('var', 'L')])), ('bin', '+', ('call', 'rank', [('var', 'H')]), ('call', 'rank', [('var', 'C')]))), ('num', 8.06882)])]), ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'correlation', [('call', 'ts_rank', [('var', 'C'), ('num', 8.44728)]), ('call', 'ts_rank', [('var', 'adv60'), ('num', 20.6966)]), ('num', 8.01266)]), ('num', 6.65053)]), ('num', 2.61957)])])}

@register_factor
@fixed_factor('alpha101_088_92d', {})
class Factor_alpha101_088_92d(PublicFactor):
    name = 'alpha101_088_92d'
    description = 'min(rank(decay_linear(((rank(O) + rank(L)) - (rank(H) + rank(C))), 8.06882)), Ts_Rank(decay_linear(correlation(Ts_Rank(C, 8.44728), Ts_Rank(adv60, 20.6966), 8.01266), 6.65053), 2.61957))；原目录：Alpha101_088；追踪：PF00088；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
