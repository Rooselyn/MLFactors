"""国泰君安 Alpha191

公式：(C<DELAY(C,5)?(C-DELAY(C,5))/DELAY(C,5):(C=DELAY(C,5)?0:(C-DELAY(C,5))/C))；原目录：GTJA_Alpha191_019；追踪：PF00119；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_019_6d', 'engine': 'alpha', 'kind': 191, 'tree': ('if', ('bin', '<', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 5.0)])), ('bin', '/', ('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 5.0)])), ('call', 'delay', [('var', 'C'), ('num', 5.0)])), ('if', ('bin', '==', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 5.0)])), ('num', 0.0), ('bin', '/', ('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 5.0)])), ('var', 'C'))))}

@register_factor
@fixed_factor('alpha191_019_6d', {})
class Factor_alpha191_019_6d(PublicFactor):
    name = 'alpha191_019_6d'
    description = '(C<DELAY(C,5)?(C-DELAY(C,5))/DELAY(C,5):(C=DELAY(C,5)?0:(C-DELAY(C,5))/C))；原目录：GTJA_Alpha191_019；追踪：PF00119；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
