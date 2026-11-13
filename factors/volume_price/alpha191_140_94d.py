"""国泰君安 Alpha191

公式：MIN(RANK(DECAYLINEAR(((RANK(O)+RANK(L))-(RANK(H)+RANK(C))),8)),TSRANK(DECAYLINEAR(CORR(TSRANK(C,8),TSRANK(MEAN(V,60),20),8),7),3))；原目录：GTJA_Alpha191_140；追踪：PF00234；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_140_94d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'min', [('call', 'rank', [('call', 'decaylinear', [('bin', '-', ('bin', '+', ('call', 'rank', [('var', 'O')]), ('call', 'rank', [('var', 'L')])), ('bin', '+', ('call', 'rank', [('var', 'H')]), ('call', 'rank', [('var', 'C')]))), ('num', 8.0)])]), ('call', 'tsrank', [('call', 'decaylinear', [('call', 'corr', [('call', 'tsrank', [('var', 'C'), ('num', 8.0)]), ('call', 'tsrank', [('call', 'mean', [('var', 'V'), ('num', 60.0)]), ('num', 20.0)]), ('num', 8.0)]), ('num', 7.0)]), ('num', 3.0)])])}

@register_factor
@fixed_factor('alpha191_140_94d', {})
class Factor_alpha191_140_94d(PublicFactor):
    name = 'alpha191_140_94d'
    description = 'MIN(RANK(DECAYLINEAR(((RANK(O)+RANK(L))-(RANK(H)+RANK(C))),8)),TSRANK(DECAYLINEAR(CORR(TSRANK(C,8),TSRANK(MEAN(V,60),20),8),7),3))；原目录：GTJA_Alpha191_140；追踪：PF00234；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
