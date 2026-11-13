"""WorldQuant Alpha101

公式：min(Ts_Rank(decay_linear(((((H + L) / 2) + C) < (L + O)), 14.7221), 18.8683), Ts_Rank(decay_linear(correlation(rank(L), rank(adv30), 7.58555), 6.94024), 6.80584))；原目录：Alpha101_092；追踪：PF00092；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_092_46d', 'engine': 'alpha', 'kind': 101, 'tree': ('call', 'min', [('call', 'ts_rank', [('call', 'decay_linear', [('bin', '<', ('bin', '+', ('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('var', 'C')), ('bin', '+', ('var', 'L'), ('var', 'O'))), ('num', 14.7221)]), ('num', 18.8683)]), ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'correlation', [('call', 'rank', [('var', 'L')]), ('call', 'rank', [('var', 'adv30')]), ('num', 7.58555)]), ('num', 6.94024)]), ('num', 6.80584)])])}

@register_factor
@fixed_factor('alpha101_092_46d', {})
class Factor_alpha101_092_46d(PublicFactor):
    name = 'alpha101_092_46d'
    description = 'min(Ts_Rank(decay_linear(((((H + L) / 2) + C) < (L + O)), 14.7221), 18.8683), Ts_Rank(decay_linear(correlation(rank(L), rank(adv30), 7.58555), 6.94024), 6.80584))；原目录：Alpha101_092；追踪：PF00092；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
