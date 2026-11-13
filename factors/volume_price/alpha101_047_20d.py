"""WorldQuant Alpha101

公式：((((rank((1 / C)) * V) / adv20) * ((H * rank((H - C))) / (sum(H, 5) / 5))) - rank((P - delay(P, 5))))；原目录：Alpha101_047；追踪：PF00047；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_047_20d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '-', ('bin', '*', ('bin', '/', ('bin', '*', ('call', 'rank', [('bin', '/', ('num', 1.0), ('var', 'C'))]), ('var', 'V')), ('var', 'adv20')), ('bin', '/', ('bin', '*', ('var', 'H'), ('call', 'rank', [('bin', '-', ('var', 'H'), ('var', 'C'))])), ('bin', '/', ('call', 'sum', [('var', 'H'), ('num', 5.0)]), ('num', 5.0)))), ('call', 'rank', [('bin', '-', ('var', 'P'), ('call', 'delay', [('var', 'P'), ('num', 5.0)]))]))}

@register_factor
@fixed_factor('alpha101_047_20d', {})
class Factor_alpha101_047_20d(PublicFactor):
    name = 'alpha101_047_20d'
    description = '((((rank((1 / C)) * V) / adv20) * ((H * rank((H - C))) / (sum(H, 5) / 5))) - rank((P - delay(P, 5))))；原目录：Alpha101_047；追踪：PF00047；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
