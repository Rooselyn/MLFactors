"""WorldQuant Alpha101

公式：(-1 * Ts_Rank(decay_linear(correlation(IndNeutralize(P, SW1), V, 3.92795), 7.89291), 5.50322))；原目录：Alpha101_058；追踪：PF00058；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
    'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1'),
}
SPEC = {'name': 'alpha101_058_13d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'correlation', [('call', 'indneutralize', [('var', 'P'), ('var', 'SW1')]), ('var', 'V'), ('num', 3.92795)]), ('num', 7.89291)]), ('num', 5.50322)]))}

@register_factor
@fixed_factor('alpha101_058_13d', {})
class Factor_alpha101_058_13d(PublicFactor):
    name = 'alpha101_058_13d'
    description = '(-1 * Ts_Rank(decay_linear(correlation(IndNeutralize(P, SW1), V, 3.92795), 7.89291), 5.50322))；原目录：Alpha101_058；追踪：PF00058；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
