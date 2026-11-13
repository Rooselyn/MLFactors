"""WorldQuant Alpha101

公式：(rank(correlation(((H * 0.876703) + (C * (1 - 0.876703))), adv30, 9.61331))^rank(correlation(Ts_Rank(((H + L) / 2), 3.70596), Ts_Rank(V, 10.1595), 7.11408)))；原目录：Alpha101_085；追踪：PF00085；[来源](https://arxiv.org/pdf/1601.00991)。
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
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'alpha101_085_38d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '^', ('call', 'rank', [('call', 'correlation', [('bin', '+', ('bin', '*', ('var', 'H'), ('num', 0.876703)), ('bin', '*', ('var', 'C'), ('bin', '-', ('num', 1.0), ('num', 0.876703)))), ('var', 'adv30'), ('num', 9.61331)])]), ('call', 'rank', [('call', 'correlation', [('call', 'ts_rank', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('num', 3.70596)]), ('call', 'ts_rank', [('var', 'V'), ('num', 10.1595)]), ('num', 7.11408)])]))}

@register_factor
@fixed_factor('alpha101_085_38d', {})
class Factor_alpha101_085_38d(PublicFactor):
    name = 'alpha101_085_38d'
    description = '(rank(correlation(((H * 0.876703) + (C * (1 - 0.876703))), adv30, 9.61331))^rank(correlation(Ts_Rank(((H + L) / 2), 3.70596), Ts_Rank(V, 10.1595), 7.11408)))；原目录：Alpha101_085；追踪：PF00085；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
