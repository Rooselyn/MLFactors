"""国泰君安 Alpha191

公式：(RANK(CORR(P,V,4))*RANK(CORR(RANK(L),RANK(MEAN(V,50)),12)))；原目录：GTJA_Alpha191_179；追踪：PF00273；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_179_61d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('call', 'rank', [('call', 'corr', [('var', 'P'), ('var', 'V'), ('num', 4.0)])]), ('call', 'rank', [('call', 'corr', [('call', 'rank', [('var', 'L')]), ('call', 'rank', [('call', 'mean', [('var', 'V'), ('num', 50.0)])]), ('num', 12.0)])]))}

@register_factor
@fixed_factor('alpha191_179_61d', {})
class Factor_alpha191_179_61d(PublicFactor):
    name = 'alpha191_179_61d'
    description = '(RANK(CORR(P,V,4))*RANK(CORR(RANK(L),RANK(MEAN(V,50)),12)))；原目录：GTJA_Alpha191_179；追踪：PF00273；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
