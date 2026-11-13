"""国泰君安 Alpha191

公式：(RANK(DELTA((((C*0.6)+(O*0.4))),1))*RANK(CORR(P,MEAN(V,150),15)))；原目录：GTJA_Alpha191_045；追踪：PF00143；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_045_164d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('call', 'rank', [('call', 'delta', [('bin', '+', ('bin', '*', ('var', 'C'), ('num', 0.6)), ('bin', '*', ('var', 'O'), ('num', 0.4))), ('num', 1.0)])]), ('call', 'rank', [('call', 'corr', [('var', 'P'), ('call', 'mean', [('var', 'V'), ('num', 150.0)]), ('num', 15.0)])]))}

@register_factor
@fixed_factor('alpha191_045_164d', {})
class Factor_alpha191_045_164d(PublicFactor):
    name = 'alpha191_045_164d'
    description = '(RANK(DELTA((((C*0.6)+(O*0.4))),1))*RANK(CORR(P,MEAN(V,150),15)))；原目录：GTJA_Alpha191_045；追踪：PF00143；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
