"""国泰君安 Alpha191

公式：SUM((O<=DELAY(O,1)?0:MAX((H-O),(O-DELAY(O,1)))),20)；原目录：GTJA_Alpha191_187；追踪：PF00281；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'alpha191_187_21d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'sum', [('if', ('bin', '<=', ('var', 'O'), ('call', 'delay', [('var', 'O'), ('num', 1.0)])), ('num', 0.0), ('call', 'max', [('bin', '-', ('var', 'H'), ('var', 'O')), ('bin', '-', ('var', 'O'), ('call', 'delay', [('var', 'O'), ('num', 1.0)]))])), ('num', 20.0)])}

@register_factor
@fixed_factor('alpha191_187_21d', {})
class Factor_alpha191_187_21d(PublicFactor):
    name = 'alpha191_187_21d'
    description = 'SUM((O<=DELAY(O,1)?0:MAX((H-O),(O-DELAY(O,1)))),20)；原目录：GTJA_Alpha191_187；追踪：PF00281；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
