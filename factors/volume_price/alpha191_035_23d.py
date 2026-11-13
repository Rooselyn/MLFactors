"""国泰君安 Alpha191

公式：(MIN(RANK(DECAYLINEAR(DELTA(O,1),15)),RANK(DECAYLINEAR(CORR((V),((O*0.65)+(O*0.35)),17),7)))*-1)；原目录：GTJA_Alpha191_035；追踪：PF00135；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_035_23d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('call', 'min', [('call', 'rank', [('call', 'decaylinear', [('call', 'delta', [('var', 'O'), ('num', 1.0)]), ('num', 15.0)])]), ('call', 'rank', [('call', 'decaylinear', [('call', 'corr', [('var', 'V'), ('bin', '+', ('bin', '*', ('var', 'O'), ('num', 0.65)), ('bin', '*', ('var', 'O'), ('num', 0.35))), ('num', 17.0)]), ('num', 7.0)])])]), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_035_23d', {})
class Factor_alpha191_035_23d(PublicFactor):
    name = 'alpha191_035_23d'
    description = '(MIN(RANK(DECAYLINEAR(DELTA(O,1),15)),RANK(DECAYLINEAR(CORR((V),((O*0.65)+(O*0.35)),17),7)))*-1)；原目录：GTJA_Alpha191_035；追踪：PF00135；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
