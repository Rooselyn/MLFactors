"""国泰君安 Alpha191

公式：(MAX(RANK(DECAYLINEAR(DELTA(P,1),12)),RANK(DECAYLINEAR(RANK(CORR((L),MEAN(V,80),8)),17)))*-1)；原目录：GTJA_Alpha191_061；追踪：PF00159；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_061_103d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('call', 'max', [('call', 'rank', [('call', 'decaylinear', [('call', 'delta', [('var', 'P'), ('num', 1.0)]), ('num', 12.0)])]), ('call', 'rank', [('call', 'decaylinear', [('call', 'rank', [('call', 'corr', [('var', 'L'), ('call', 'mean', [('var', 'V'), ('num', 80.0)]), ('num', 8.0)])]), ('num', 17.0)])])]), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_061_103d', {})
class Factor_alpha191_061_103d(PublicFactor):
    name = 'alpha191_061_103d'
    description = '(MAX(RANK(DECAYLINEAR(DELTA(P,1),12)),RANK(DECAYLINEAR(RANK(CORR((L),MEAN(V,80),8)),17)))*-1)；原目录：GTJA_Alpha191_061；追踪：PF00159；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
