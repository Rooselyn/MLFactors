"""国泰君安 Alpha191

公式：((RANK(CORR(SUM(((H+L)/2),20),SUM(MEAN(V,60),20),9))<RANK(CORR(L,V,6)))*-1)；原目录：GTJA_Alpha191_123；追踪：PF00217；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_123_87d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '<', ('call', 'rank', [('call', 'corr', [('call', 'sum', [('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('num', 20.0)]), ('call', 'sum', [('call', 'mean', [('var', 'V'), ('num', 60.0)]), ('num', 20.0)]), ('num', 9.0)])]), ('call', 'rank', [('call', 'corr', [('var', 'L'), ('var', 'V'), ('num', 6.0)])])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_123_87d', {})
class Factor_alpha191_123_87d(PublicFactor):
    name = 'alpha191_123_87d'
    description = '((RANK(CORR(SUM(((H+L)/2),20),SUM(MEAN(V,60),20),9))<RANK(CORR(L,V,6)))*-1)；原目录：GTJA_Alpha191_123；追踪：PF00217；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
