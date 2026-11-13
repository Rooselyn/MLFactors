"""WorldQuant Alpha101

公式：min(rank(decay_linear(((((H + L) / 2) + H) - (P + H)), 20.0451)), rank(decay_linear(correlation(((H + L) / 2), adv40, 3.1614), 5.64125)))；原目录：Alpha101_077；追踪：PF00077；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_077_46d', 'engine': 'alpha', 'kind': 101, 'tree': ('call', 'min', [('call', 'rank', [('call', 'decay_linear', [('bin', '-', ('bin', '+', ('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('var', 'H')), ('bin', '+', ('var', 'P'), ('var', 'H'))), ('num', 20.0451)])]), ('call', 'rank', [('call', 'decay_linear', [('call', 'correlation', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('var', 'adv40'), ('num', 3.1614)]), ('num', 5.64125)])])])}

@register_factor
@fixed_factor('alpha101_077_46d', {})
class Factor_alpha101_077_46d(PublicFactor):
    name = 'alpha101_077_46d'
    description = 'min(rank(decay_linear(((((H + L) / 2) + H) - (P + H)), 20.0451)), rank(decay_linear(correlation(((H + L) / 2), adv40, 3.1614), 5.64125)))；原目录：Alpha101_077；追踪：PF00077；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
