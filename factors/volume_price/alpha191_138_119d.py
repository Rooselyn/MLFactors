"""国泰君安 Alpha191

公式：((RANK(DECAYLINEAR(DELTA((((L*0.7)+(P*0.3))),3),20))-TSRANK(DECAYLINEAR(TSRANK(CORR(TSRANK(L,8),TSRANK(MEAN(V,60),17),5),19),16),7))*-1)；原目录：GTJA_Alpha191_138；追踪：PF00232；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_138_119d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '-', ('call', 'rank', [('call', 'decaylinear', [('call', 'delta', [('bin', '+', ('bin', '*', ('var', 'L'), ('num', 0.7)), ('bin', '*', ('var', 'P'), ('num', 0.3))), ('num', 3.0)]), ('num', 20.0)])]), ('call', 'tsrank', [('call', 'decaylinear', [('call', 'tsrank', [('call', 'corr', [('call', 'tsrank', [('var', 'L'), ('num', 8.0)]), ('call', 'tsrank', [('call', 'mean', [('var', 'V'), ('num', 60.0)]), ('num', 17.0)]), ('num', 5.0)]), ('num', 19.0)]), ('num', 16.0)]), ('num', 7.0)])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_138_119d', {})
class Factor_alpha191_138_119d(PublicFactor):
    name = 'alpha191_138_119d'
    description = '((RANK(DECAYLINEAR(DELTA((((L*0.7)+(P*0.3))),3),20))-TSRANK(DECAYLINEAR(TSRANK(CORR(TSRANK(L,8),TSRANK(MEAN(V,60),17),5),19),16),7))*-1)；原目录：GTJA_Alpha191_138；追踪：PF00232；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
