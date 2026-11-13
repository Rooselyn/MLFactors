"""国泰君安 Alpha191

公式：(RANK((O-TSMIN(O,12)))<RANK((RANK(CORR(SUM(((H+L)/2),19),SUM(MEAN(V,40),19),13))^5)))；原目录：GTJA_Alpha191_056；追踪：PF00154；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_056_70d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '<', ('call', 'rank', [('bin', '-', ('var', 'O'), ('call', 'tsmin', [('var', 'O'), ('num', 12.0)]))]), ('call', 'rank', [('bin', '^', ('call', 'rank', [('call', 'corr', [('call', 'sum', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('num', 19.0)]), ('call', 'sum', [('call', 'mean', [('var', 'V'), ('num', 40.0)]), ('num', 19.0)]), ('num', 13.0)])]), ('num', 5.0))]))}

@register_factor
@fixed_factor('alpha191_056_70d', {})
class Factor_alpha191_056_70d(PublicFactor):
    name = 'alpha191_056_70d'
    description = '(RANK((O-TSMIN(O,12)))<RANK((RANK(CORR(SUM(((H+L)/2),19),SUM(MEAN(V,40),19),13))^5)))；原目录：GTJA_Alpha191_056；追踪：PF00154；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
