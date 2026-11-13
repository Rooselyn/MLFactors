"""国泰君安 Alpha191

公式：(RANK(CORR(DELAY((O-C),1),C,200))+RANK((O-C)))；原目录：GTJA_Alpha191_184；追踪：PF00278；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'alpha191_184_201d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '+', ('call', 'rank', [('call', 'corr', [('call', 'delay', [('bin', '-', ('var', 'O'), ('var', 'C')), ('num', 1.0)]), ('var', 'C'), ('num', 200.0)])]), ('call', 'rank', [('bin', '-', ('var', 'O'), ('var', 'C'))]))}

@register_factor
@fixed_factor('alpha191_184_201d', {})
class Factor_alpha191_184_201d(PublicFactor):
    name = 'alpha191_184_201d'
    description = '(RANK(CORR(DELAY((O-C),1),C,200))+RANK((O-C)))；原目录：GTJA_Alpha191_184；追踪：PF00278；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
