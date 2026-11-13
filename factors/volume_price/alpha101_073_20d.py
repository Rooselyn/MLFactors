"""WorldQuant Alpha101

公式：(max(rank(decay_linear(delta(P, 4.72775), 2.91864)), Ts_Rank(decay_linear(((delta(((O * 0.147155) + (L * (1 - 0.147155))), 2.03608) / ((O * 0.147155) + (L * (1 - 0.147155)))) * -1), 3.33829), 16.7411)) * -1)；原目录：Alpha101_073；追踪：PF00073；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_073_20d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('call', 'max', [('call', 'rank', [('call', 'decay_linear', [('call', 'delta', [('var', 'P'), ('num', 4.72775)]), ('num', 2.91864)])]), ('call', 'ts_rank', [('call', 'decay_linear', [('bin', '*', ('bin', '/', ('call', 'delta', [('bin', '+', ('bin', '*', ('var', 'O'), ('num', 0.147155)), ('bin', '*', ('var', 'L'), ('bin', '-', ('num', 1.0), ('num', 0.147155)))), ('num', 2.03608)]), ('bin', '+', ('bin', '*', ('var', 'O'), ('num', 0.147155)), ('bin', '*', ('var', 'L'), ('bin', '-', ('num', 1.0), ('num', 0.147155))))), ('unary', '-', ('num', 1.0))), ('num', 3.33829)]), ('num', 16.7411)])]), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha101_073_20d', {})
class Factor_alpha101_073_20d(PublicFactor):
    name = 'alpha101_073_20d'
    description = '(max(rank(decay_linear(delta(P, 4.72775), 2.91864)), Ts_Rank(decay_linear(((delta(((O * 0.147155) + (L * (1 - 0.147155))), 2.03608) / ((O * 0.147155) + (L * (1 - 0.147155)))) * -1), 3.33829), 16.7411)) * -1)；原目录：Alpha101_073；追踪：PF00073；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
