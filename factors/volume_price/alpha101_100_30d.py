"""WorldQuant Alpha101

公式：(0 - (1 * (((1.5 * scale(indneutralize(indneutralize(rank(((((C - L) - (H - C)) / (H - L)) * V)), SW3), SW3))) - scale(indneutralize((correlation(C, rank(adv20), 5) - rank(ts_argmin(C, 30))), SW3))) * (V / adv20))))；原目录：Alpha101_100；追踪：PF00100；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'industry_sw_3': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_3'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'alpha101_100_30d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '-', ('num', 0.0), ('bin', '*', ('num', 1.0), ('bin', '*', ('bin', '-', ('bin', '*', ('num', 1.5), ('call', 'scale', [('call', 'indneutralize', [('call', 'indneutralize', [('call', 'rank', [('bin', '*', ('bin', '/', ('bin', '-', ('bin', '-', ('var', 'C'), ('var', 'L')), ('bin', '-', ('var', 'H'), ('var', 'C'))), ('bin', '-', ('var', 'H'), ('var', 'L'))), ('var', 'V'))]), ('var', 'SW3')]), ('var', 'SW3')])])), ('call', 'scale', [('call', 'indneutralize', [('bin', '-', ('call', 'correlation', [('var', 'C'), ('call', 'rank', [('var', 'adv20')]), ('num', 5.0)]), ('call', 'rank', [('call', 'ts_argmin', [('var', 'C'), ('num', 30.0)])])), ('var', 'SW3')])])), ('bin', '/', ('var', 'V'), ('var', 'adv20')))))}

@register_factor
@fixed_factor('alpha101_100_30d', {})
class Factor_alpha101_100_30d(PublicFactor):
    name = 'alpha101_100_30d'
    description = '(0 - (1 * (((1.5 * scale(indneutralize(indneutralize(rank(((((C - L) - (H - C)) / (H - L)) * V)), SW3), SW3))) - scale(indneutralize((correlation(C, rank(adv20), 5) - rank(ts_argmin(C, 30))), SW3))) * (V / adv20))))；原目录：Alpha101_100；追踪：PF00100；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
