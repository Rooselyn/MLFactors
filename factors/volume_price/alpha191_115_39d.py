"""国泰君安 Alpha191

公式：(RANK(CORR(((H*0.9)+(C*0.1)),MEAN(V,30),10))^RANK(CORR(TSRANK(((H+L)/2),4),TSRANK(V,10),7)))；原目录：GTJA_Alpha191_115；追踪：PF00210；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_115_39d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '^', ('call', 'rank', [('call', 'corr', [('bin', '+', ('bin', '*', ('var', 'H'), ('num', 0.9)), ('bin', '*', ('var', 'C'), ('num', 0.1))), ('call', 'mean', [('var', 'V'), ('num', 30.0)]), ('num', 10.0)])]), ('call', 'rank', [('call', 'corr', [('call', 'tsrank', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('num', 4.0)]), ('call', 'tsrank', [('var', 'V'), ('num', 10.0)]), ('num', 7.0)])]))}

@register_factor
@fixed_factor('alpha191_115_39d', {})
class Factor_alpha191_115_39d(PublicFactor):
    name = 'alpha191_115_39d'
    description = '(RANK(CORR(((H*0.9)+(C*0.1)),MEAN(V,30),10))^RANK(CORR(TSRANK(((H+L)/2),4),TSRANK(V,10),7)))；原目录：GTJA_Alpha191_115；追踪：PF00210；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
