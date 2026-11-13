"""WorldQuant Alpha101

公式：(rank(Ts_ArgMax(SignedPower(((R < 0) ? stddev(R, 20) : C), 2.), 5)) - 0.5)；原目录：Alpha101_001；追踪：PF00001；[来源](https://arxiv.org/pdf/1601.00991)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha101_001_25d', 'engine': 'alpha', 'kind': 101, 'tree': ('bin', '-', ('call', 'rank', [('call', 'ts_argmax', [('call', 'signedpower', [('if', ('bin', '<', ('var', 'R'), ('num', 0.0)), ('call', 'stddev', [('var', 'R'), ('num', 20.0)]), ('var', 'C')), ('num', 2.0)]), ('num', 5.0)])]), ('num', 0.5))}

@register_factor
@fixed_factor('alpha101_001_25d', {})
class Factor_alpha101_001_25d(PublicFactor):
    name = 'alpha101_001_25d'
    description = '(rank(Ts_ArgMax(SignedPower(((R < 0) ? stddev(R, 20) : C), 2.), 5)) - 0.5)；原目录：Alpha101_001；追踪：PF00001；[来源](https://arxiv.org/pdf/1601.00991)。'
    INPUTS = INPUTS
    SPEC = SPEC
