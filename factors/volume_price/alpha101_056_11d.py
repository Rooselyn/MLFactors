"""WorldQuant Alpha101

公式：(0 - (1 * (rank((sum(R, 10) / sum(sum(R, 2), 3))) * rank((R * MC)))))；原目录：Alpha101_056；追踪：PF00056；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha101_056_11d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '-', ('num', 0.0), ('bin', '*', ('num', 1.0), ('bin', '*', ('call', 'rank', [('bin', '/', ('call', 'sum', [('var', 'R'), ('num', 10.0)]), ('call', 'sum', [('call', 'sum', [('var', 'R'), ('num', 2.0)]), ('num', 3.0)]))]), ('call', 'rank', [('bin', '*', ('var', 'R'), ('var', 'MC'))]))))}

@register_factor
@fixed_factor('alpha101_056_11d', {})
class Factor_alpha101_056_11d(PublicFactor):
    name = 'alpha101_056_11d'
    description = '(0 - (1 * (rank((sum(R, 10) / sum(sum(R, 2), 3))) * rank((R * MC)))))；原目录：Alpha101_056；追踪：PF00056；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
