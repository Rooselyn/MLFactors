"""国泰君安 Alpha191

公式：(TSRANK(DECAYLINEAR(CORR(((L)),MEAN(V,10),7),6),4)+TSRANK(DECAYLINEAR(DELTA((P),3),10),15))；原目录：GTJA_Alpha191_044；追踪：PF00142；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_044_27d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '+', ('call', 'tsrank', [('call', 'decaylinear', [('call', 'corr', [('var', 'L'), ('call', 'mean', [('var', 'V'), ('num', 10.0)]), ('num', 7.0)]), ('num', 6.0)]), ('num', 4.0)]), ('call', 'tsrank', [('call', 'decaylinear', [('call', 'delta', [('var', 'P'), ('num', 3.0)]), ('num', 10.0)]), ('num', 15.0)]))}

@register_factor
@fixed_factor('alpha191_044_27d', {})
class Factor_alpha191_044_27d(PublicFactor):
    name = 'alpha191_044_27d'
    description = '(TSRANK(DECAYLINEAR(CORR(((L)),MEAN(V,10),7),6),4)+TSRANK(DECAYLINEAR(DELTA((P),3),10),15))；原目录：GTJA_Alpha191_044；追踪：PF00142；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
