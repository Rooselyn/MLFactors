"""国泰君安 Alpha191

公式：((RANK(CORR(C,SUM(MEAN(V,30),37),15))<RANK(CORR(RANK(((H*0.1)+(P*0.9))),RANK(V),11)))*-1)；原目录：GTJA_Alpha191_101；追踪：PF00198；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_101_80d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '<', ('call', 'rank', [('call', 'corr', [('var', 'C'), ('call', 'sum', [('call', 'mean', [('var', 'V'), ('num', 30.0)]), ('num', 37.0)]), ('num', 15.0)])]), ('call', 'rank', [('call', 'corr', [('call', 'rank', [('bin', '+', ('bin', '*', ('var', 'H'), ('num', 0.1)), ('bin', '*', ('var', 'P'), ('num', 0.9)))]), ('call', 'rank', [('var', 'V')]), ('num', 11.0)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_101_80d', {})
class Factor_alpha191_101_80d(PublicFactor):
    name = 'alpha191_101_80d'
    description = '((RANK(CORR(C,SUM(MEAN(V,30),37),15))<RANK(CORR(RANK(((H*0.1)+(P*0.9))),RANK(V),11)))*-1)；原目录：GTJA_Alpha191_101；追踪：PF00198；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
