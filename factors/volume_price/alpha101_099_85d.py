"""WorldQuant Alpha101

公式：((rank(correlation(sum(((H + L) / 2), 19.8975), sum(adv60, 19.8975), 8.8136)) < rank(correlation(L, V, 6.28259))) * -1)；原目录：Alpha101_099；追踪：PF00099；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
}
SPEC = {'name': 'alpha101_099_85d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('bin', '<', ('call', 'rank', [('call', 'correlation', [('call', 'sum', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('num', 19.8975)]), ('call', 'sum', [('var', 'adv60'), ('num', 19.8975)]), ('num', 8.8136)])]), ('call', 'rank', [('call', 'correlation', [('var', 'L'), ('var', 'V'), ('num', 6.28259)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_099_85d', {})
class Factor_alpha101_099_85d(PublicFactor):
    name = 'alpha101_099_85d'
    description = '((rank(correlation(sum(((H + L) / 2), 19.8975), sum(adv60, 19.8975), 8.8136)) < rank(correlation(L, V, 6.28259))) * -1)；原目录：Alpha101_099；追踪：PF00099；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
