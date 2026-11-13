"""国泰君安 Alpha191

公式：((RANK(DECAYLINEAR(DELTA((C),2),8))-RANK(DECAYLINEAR(CORR(((P*0.3)+(O*0.7)),SUM(MEAN(V,180),37),14),12)))*-1)；原目录：GTJA_Alpha191_039；追踪：PF00137；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_039_240d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '-', ('call', 'rank', [('call', 'decaylinear', [('call', 'delta', [('var', 'C'), ('num', 2.0)]), ('num', 8.0)])]), ('call', 'rank', [('call', 'decaylinear', [('call', 'corr', [('bin', '+', ('bin', '*', ('var', 'P'), ('num', 0.3)), ('bin', '*', ('var', 'O'), ('num', 0.7))), ('call', 'sum', [('call', 'mean', [('var', 'V'), ('num', 180.0)]), ('num', 37.0)]), ('num', 14.0)]), ('num', 12.0)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_039_240d', {})
class Factor_alpha191_039_240d(PublicFactor):
    name = 'alpha191_039_240d'
    description = '((RANK(DECAYLINEAR(DELTA((C),2),8))-RANK(DECAYLINEAR(CORR(((P*0.3)+(O*0.7)),SUM(MEAN(V,180),37),14),12)))*-1)；原目录：GTJA_Alpha191_039；追踪：PF00137；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
