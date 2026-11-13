"""国泰君安 Alpha191

公式：(RANK(CORR(RANK(H),RANK(MEAN(V,15)),9))*-1)；原目录：GTJA_Alpha191_141；追踪：PF00235；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_141_23d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('call', 'rank', [('call', 'corr', [('call', 'rank', [('var', 'H')]), ('call', 'rank', [('call', 'mean', [('var', 'V'), ('num', 15.0)])]), ('num', 9.0)])]), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_141_23d', {})
class Factor_alpha191_141_23d(PublicFactor):
    name = 'alpha191_141_23d'
    description = '(RANK(CORR(RANK(H),RANK(MEAN(V,15)),9))*-1)；原目录：GTJA_Alpha191_141；追踪：PF00235；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
