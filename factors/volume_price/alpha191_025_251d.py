"""国泰君安 Alpha191

公式：((-1*RANK((DELTA(C,7)*(1-RANK(DECAYLINEAR((V/MEAN(V,20)),9))))))*(1+RANK(SUM(R,250))))；原目录：GTJA_Alpha191_025；追踪：PF00125；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_025_251d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('bin', '*', ('call', 'delta', [('var', 'C'), ('num', 7.0)]), ('bin', '-', ('num', 1.0), ('call', 'rank', [('call', 'decaylinear', [('bin', '/', ('var', 'V'), ('call', 'mean', [('var', 'V'), ('num', 20.0)])), ('num', 9.0)])])))])), ('bin', '+', ('num', 1.0), ('call', 'rank', [('call', 'sum', [('var', 'R'), ('num', 250.0)])])))}

@register_factor
@fixed_factor('alpha191_025_251d', {})
class Factor_alpha191_025_251d(PublicFactor):
    name = 'alpha191_025_251d'
    description = '((-1*RANK((DELTA(C,7)*(1-RANK(DECAYLINEAR((V/MEAN(V,20)),9))))))*(1+RANK(SUM(R,250))))；原目录：GTJA_Alpha191_025；追踪：PF00125；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
