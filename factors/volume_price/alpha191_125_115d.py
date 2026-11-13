"""国泰君安 Alpha191

公式：(RANK(DECAYLINEAR(CORR((P),MEAN(V,80),17),20))/RANK(DECAYLINEAR(DELTA(((C*0.5)+(P*0.5)),3),16)))；原目录：GTJA_Alpha191_125；追踪：PF00219；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_125_115d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '/', ('call', 'rank', [('call', 'decaylinear', [('call', 'corr', [('var', 'P'), ('call', 'mean', [('var', 'V'), ('num', 80.0)]), ('num', 17.0)]), ('num', 20.0)])]), ('call', 'rank', [('call', 'decaylinear', [('call', 'delta', [('bin', '+', ('bin', '*', ('var', 'C'), ('num', 0.5)), ('bin', '*', ('var', 'P'), ('num', 0.5))), ('num', 3.0)]), ('num', 16.0)])]))}

@register_factor
@fixed_factor('alpha191_125_115d', {})
class Factor_alpha191_125_115d(PublicFactor):
    name = 'alpha191_125_115d'
    description = '(RANK(DECAYLINEAR(CORR((P),MEAN(V,80),17),20))/RANK(DECAYLINEAR(DELTA(((C*0.5)+(P*0.5)),3),16)))；原目录：GTJA_Alpha191_125；追踪：PF00219；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
