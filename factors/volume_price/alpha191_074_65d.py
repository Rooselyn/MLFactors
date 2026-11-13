"""国泰君安 Alpha191

公式：(RANK(CORR(SUM(((L*0.35)+(P*0.65)),20),SUM(MEAN(V,40),20),7))+RANK(CORR(RANK(P),RANK(V),6)))；原目录：GTJA_Alpha191_074；追踪：PF00172；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_074_65d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '+', ('call', 'rank', [('call', 'corr', [('call', 'sum', [('bin', '+', ('bin', '*', ('var', 'L'), ('num', 0.35)), ('bin', '*', ('var', 'P'), ('num', 0.65))), ('num', 20.0)]), ('call', 'sum', [('call', 'mean', [('var', 'V'), ('num', 40.0)]), ('num', 20.0)]), ('num', 7.0)])]), ('call', 'rank', [('call', 'corr', [('call', 'rank', [('var', 'P')]), ('call', 'rank', [('var', 'V')]), ('num', 6.0)])]))}

@register_factor
@fixed_factor('alpha191_074_65d', {})
class Factor_alpha191_074_65d(PublicFactor):
    name = 'alpha191_074_65d'
    description = '(RANK(CORR(SUM(((L*0.35)+(P*0.65)),20),SUM(MEAN(V,40),20),7))+RANK(CORR(RANK(P),RANK(V),6)))；原目录：GTJA_Alpha191_074；追踪：PF00172；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
