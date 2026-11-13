"""国泰君安 Alpha191

公式：(-1*((RANK(((SIGN((C-DELAY(C,1)))+SIGN((DELAY(C,1)-DELAY(C,2))))+SIGN((DELAY(C,2)-DELAY(C,3))))))*SUM(V,5))/SUM(V,20))；原目录：GTJA_Alpha191_048；追踪：PF00146；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_048_20d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '/', ('bin', '*', ('unary', '-', ('num', 1.0)), ('bin', '*', ('call', 'rank', [('bin', '+', ('bin', '+', ('call', 'sign', [('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('call', 'sign', [('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 1.0)]), ('call', 'delay', [('var', 'C'), ('num', 2.0)]))])), ('call', 'sign', [('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 2.0)]), ('call', 'delay', [('var', 'C'), ('num', 3.0)]))]))]), ('call', 'sum', [('var', 'V'), ('num', 5.0)]))), ('call', 'sum', [('var', 'V'), ('num', 20.0)]))}

@register_factor
@fixed_factor('alpha191_048_20d', {})
class Factor_alpha191_048_20d(PublicFactor):
    name = 'alpha191_048_20d'
    description = '(-1*((RANK(((SIGN((C-DELAY(C,1)))+SIGN((DELAY(C,1)-DELAY(C,2))))+SIGN((DELAY(C,2)-DELAY(C,3))))))*SUM(V,5))/SUM(V,20))；原目录：GTJA_Alpha191_048；追踪：PF00146；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
