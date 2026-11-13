"""WorldQuant Alpha101

公式：((rank(correlation(sum(((O * 0.178404) + (L * (1 - 0.178404))), 12.7054), sum(adv120, 12.7054), 16.6208)) < rank(delta(((((H + L) / 2) * 0.178404) + (P * (1 - 0.178404))), 3.69741))) * -1)；原目录：Alpha101_064；追踪：PF00064；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_064_146d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '<', ('call', 'rank', [('call', 'correlation', [('call', 'sum', [('bin', '+', ('bin', '*', ('var', 'O'), ('num', 0.178404)), ('bin', '*', ('var', 'L'), ('bin', '-', ('num', 1.0), ('num', 0.178404)))), ('num', 12.7054)]), ('call', 'sum', [('var', 'adv120'), ('num', 12.7054)]), ('num', 16.6208)])]), ('call', 'rank', [('call', 'delta', [('bin', '+', ('bin', '*', ('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('num', 0.178404)), ('bin', '*', ('var', 'P'), ('bin', '-', ('num', 1.0), ('num', 0.178404)))), ('num', 3.69741)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_064_146d', {})
class Factor_alpha101_064_146d(PublicFactor):
    name = 'alpha101_064_146d'
    description = '((rank(correlation(sum(((O * 0.178404) + (L * (1 - 0.178404))), 12.7054), sum(adv120, 12.7054), 16.6208)) < rank(delta(((((H + L) / 2) * 0.178404) + (P * (1 - 0.178404))), 3.69741))) * -1)；原目录：Alpha101_064；追踪：PF00064；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
