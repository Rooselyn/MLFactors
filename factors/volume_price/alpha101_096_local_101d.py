"""WorldQuant Alpha101

公式：(max(Ts_Rank(decay_linear(correlation(rank(P), rank(V), 3.83878), 4.16783), 8.38151), Ts_Rank(decay_linear(Ts_ArgMax(correlation(Ts_Rank(C, 7.45404), Ts_Rank(adv60, 4.13242), 3.65459), 12.6556), 14.0365), 13.4143)) * -1)；原目录：Alpha101_096；追踪：PF00096；[来源](https://arxiv.org/pdf/1601.00991)。
本地退化约定：仅在相关窗口完整且至少一列为常数时，相关系数置0；真实缺失及预热保持NaN；有限相关系数限制在[-1,1]。原始严格版本不采用此约定。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha101_096_local_101d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '*', ('call', 'max', [('call', 'ts_rank', [('call', 'decay_linear', [('call', 'correlation', [('call', 'rank', [('var', 'P')]), ('call', 'rank', [('var', 'V')]), ('num', 3.83878)]), ('num', 4.16783)]), ('num', 8.38151)]), ('call', 'ts_rank', [('call', 'decay_linear', [('call', 'ts_argmax', [('call', 'correlation', [('call', 'ts_rank', [('var', 'C'), ('num', 7.45404)]), ('call', 'ts_rank', [('var', 'adv60'), ('num', 4.13242)]), ('num', 3.65459)]), ('num', 12.6556)]), ('num', 14.0365)]), ('num', 13.4143)])]), ('unary', '-', ('num', 1.0))), 'constant_correlation_zero': True}

@register_factor
@fixed_factor('alpha101_096_local_101d', {})
class Factor_alpha101_096_local_101d(PublicFactor):
    name = 'alpha101_096_local_101d'
    description = '(max(Ts_Rank(decay_linear(correlation(rank(P), rank(V), 3.83878), 4.16783), 8.38151), Ts_Rank(decay_linear(Ts_ArgMax(correlation(Ts_Rank(C, 7.45404), Ts_Rank(adv60, 4.13242), 3.65459), 12.6556), 14.0365), 13.4143)) * -1)；原目录：Alpha101_096；追踪：PF00096；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
