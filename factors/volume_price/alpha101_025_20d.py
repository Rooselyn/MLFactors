"""WorldQuant Alpha101

公式：rank(((((-1 * R) * adv20) * P) * (H - C)))；原目录：Alpha101_025；追踪：PF00025；[来源](https://arxiv.org/pdf/1601.00991)。
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
SPEC = {'name': 'alpha101_025_20d', 'engine': 'alpha', 'kind': 101, 'tree': ('call', 'rank', [('bin', '*', ('bin', '*', ('bin', '*', ('bin', '*', ('unary', '-', ('num', 1.0)), ('var', 'R')), ('var', 'adv20')), ('var', 'P')), ('bin', '-', ('var', 'H'), ('var', 'C')))])}

@register_factor
@fixed_factor('alpha101_025_20d', {})
class Factor_alpha101_025_20d(PublicFactor):
    name = 'alpha101_025_20d'
    description = 'rank(((((-1 * R) * adv20) * P) * (H - C)))；原目录：Alpha101_025；追踪：PF00025；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
