"""国泰君安 Alpha191

公式：(-1*SUM(RANK(CORR(RANK(H),RANK(V),3)),3))；原目录：GTJA_Alpha191_032；追踪：PF00132；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_032_5d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'sum', [('call', 'rank', [('call', 'corr', [('call', 'rank', [('var', 'H')]), ('call', 'rank', [('var', 'V')]), ('num', 3.0)])]), ('num', 3.0)]))}

@register_factor
@fixed_factor('alpha191_032_5d', {})
class Factor_alpha191_032_5d(PublicFactor):
    name = 'alpha191_032_5d'
    description = '(-1*SUM(RANK(CORR(RANK(H),RANK(V),3)),3))；原目录：GTJA_Alpha191_032；追踪：PF00132；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
