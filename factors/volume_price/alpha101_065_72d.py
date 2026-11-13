"""WorldQuant Alpha101

公式：((rank(correlation(((O * 0.00817205) + (P * (1 - 0.00817205))), sum(adv60, 8.6911), 6.40374)) < rank((O - ts_min(O, 13.635)))) * -1)；原目录：Alpha101_065；追踪：PF00065；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_065_72d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '<', ('call', 'rank', [('call', 'correlation', [('bin', '+', ('bin', '*', ('var', 'O'), ('num', 0.00817205)), ('bin', '*', ('var', 'P'), ('bin', '-', ('num', 1.0), ('num', 0.00817205)))), ('call', 'sum', [('var', 'adv60'), ('num', 8.6911)]), ('num', 6.40374)])]), ('call', 'rank', [('bin', '-', ('var', 'O'), ('call', 'ts_min', [('var', 'O'), ('num', 13.635)]))])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_065_72d', {})
class Factor_alpha101_065_72d(PublicFactor):
    name = 'alpha101_065_72d'
    description = '((rank(correlation(((O * 0.00817205) + (P * (1 - 0.00817205))), sum(adv60, 8.6911), 6.40374)) < rank((O - ts_min(O, 13.635)))) * -1)；原目录：Alpha101_065；追踪：PF00065；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
