"""国泰君安 Alpha191

公式：((RANK(CORR((O),SUM(MEAN(V,60),9),6))<RANK((O-TSMIN(O,14))))*-1)；原目录：GTJA_Alpha191_148；追踪：PF00242；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_148_73d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '<', ('call', 'rank', [('call', 'corr', [('var', 'O'), ('call', 'sum', [('call', 'mean', [('var', 'V'), ('num', 60.0)]), ('num', 9.0)]), ('num', 6.0)])]), ('call', 'rank', [('bin', '-', ('var', 'O'), ('call', 'tsmin', [('var', 'O'), ('num', 14.0)]))])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_148_73d', {})
class Factor_alpha191_148_73d(PublicFactor):
    name = 'alpha191_148_73d'
    description = '((RANK(CORR((O),SUM(MEAN(V,60),9),6))<RANK((O-TSMIN(O,14))))*-1)；原目录：GTJA_Alpha191_148；追踪：PF00242；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
