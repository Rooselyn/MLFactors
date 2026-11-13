"""国泰君安 Alpha191

公式：(-1*((RANK((SUM(DELAY(C,5),20)/20))*CORR(C,V,2))*RANK(CORR(SUM(C,5),SUM(C,20),2))))；原目录：GTJA_Alpha191_113；追踪：PF00209；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_113_25d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('bin', '*', ('bin', '*', ('call', 'rank', [('bin', '/', ('call', 'sum', [('call', 'delay', [('var', 'C'), ('num', 5.0)]), ('num', 20.0)]), ('num', 20.0))]), ('call', 'corr', [('var', 'C'), ('var', 'V'), ('num', 2.0)])), ('call', 'rank', [('call', 'corr', [('call', 'sum', [('var', 'C'), ('num', 5.0)]), ('call', 'sum', [('var', 'C'), ('num', 20.0)]), ('num', 2.0)])])))}

@register_factor
@fixed_factor('alpha191_113_25d', {})
class Factor_alpha191_113_25d(PublicFactor):
    name = 'alpha191_113_25d'
    description = '(-1*((RANK((SUM(DELAY(C,5),20)/20))*CORR(C,V,2))*RANK(CORR(SUM(C,5),SUM(C,20),2))))；原目录：GTJA_Alpha191_113；追踪：PF00209；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
