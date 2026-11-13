"""国泰君安 Alpha191

公式：(RANK(DECAYLINEAR(CORR(((H+L)/2),MEAN(V,40),9),10))/RANK(DECAYLINEAR(CORR(RANK(P),RANK(V),7),3)))；原目录：GTJA_Alpha191_130；追踪：PF00224；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_130_57d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '/', ('call', 'rank', [('call', 'decaylinear', [('call', 'corr', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('call', 'mean', [('var', 'V'), ('num', 40.0)]), ('num', 9.0)]), ('num', 10.0)])]), ('call', 'rank', [('call', 'decaylinear', [('call', 'corr', [('call', 'rank', [('var', 'P')]), ('call', 'rank', [('var', 'V')]), ('num', 7.0)]), ('num', 3.0)])]))}

@register_factor
@fixed_factor('alpha191_130_57d', {})
class Factor_alpha191_130_57d(PublicFactor):
    name = 'alpha191_130_57d'
    description = '(RANK(DECAYLINEAR(CORR(((H+L)/2),MEAN(V,40),9),10))/RANK(DECAYLINEAR(CORR(RANK(P),RANK(V),7),3)))；原目录：GTJA_Alpha191_130；追踪：PF00224；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
