"""WorldQuant Alpha101

公式：scale(((correlation(adv20, L, 5) + ((H + L) / 2)) - C))；原目录：Alpha101_028；追踪：PF00028；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_028_24d', 'engine': 'alpha', 'kind': 101, 'tree': ('call', 'scale', [('bin', '-', ('bin', '+', ('call', 'correlation', [('var', 'adv20'), ('var', 'L'), ('num', 5.0)]), ('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0))), ('var', 'C'))])}

@register_factor
@fixed_factor('alpha101_028_24d', {})
class Factor_alpha101_028_24d(PublicFactor):
    name = 'alpha101_028_24d'
    description = 'scale(((correlation(adv20, L, 5) + ((H + L) / 2)) - C))；原目录：Alpha101_028；追踪：PF00028；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
