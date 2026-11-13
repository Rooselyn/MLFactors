"""国泰君安 Alpha191

公式：(MAX(RANK(DECAYLINEAR(DELTA(((C*0.35)+(P*0.65)),2),3)),TSRANK(DECAYLINEAR(ABS(CORR((MEAN(V,180)),C,13)),5),15))*-1)；原目录：GTJA_Alpha191_092；追踪：PF00189；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_092_210d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('call', 'max', [('call', 'rank', [('call', 'decaylinear', [('call', 'delta', [('bin', '+', ('bin', '*', ('var', 'C'), ('num', 0.35)), ('bin', '*', ('var', 'P'), ('num', 0.65))), ('num', 2.0)]), ('num', 3.0)])]), ('call', 'tsrank', [('call', 'decaylinear', [('call', 'abs', [('call', 'corr', [('call', 'mean', [('var', 'V'), ('num', 180.0)]), ('var', 'C'), ('num', 13.0)])]), ('num', 5.0)]), ('num', 15.0)])]), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_092_210d', {})
class Factor_alpha191_092_210d(PublicFactor):
    name = 'alpha191_092_210d'
    description = '(MAX(RANK(DECAYLINEAR(DELTA(((C*0.35)+(P*0.65)),2),3)),TSRANK(DECAYLINEAR(ABS(CORR((MEAN(V,180)),C,13)),5),15))*-1)；原目录：GTJA_Alpha191_092；追踪：PF00189；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
