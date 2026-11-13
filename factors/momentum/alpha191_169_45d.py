"""国泰君安 Alpha191

公式：SMA(MEAN(DELAY(SMA(C-DELAY(C,1),9,1),1),12)-MEAN(DELAY(SMA(C-DELAY(C,1),9,1),1),26),10,1)；原目录：GTJA_Alpha191_169；追踪：PF00263；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_169_45d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'sma', [('bin', '-', ('call', 'mean', [('call', 'delay', [('call', 'sma', [('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 1.0)])), ('num', 9.0), ('num', 1.0)]), ('num', 1.0)]), ('num', 12.0)]), ('call', 'mean', [('call', 'delay', [('call', 'sma', [('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 1.0)])), ('num', 9.0), ('num', 1.0)]), ('num', 1.0)]), ('num', 26.0)])), ('num', 10.0), ('num', 1.0)])}

@register_factor
@fixed_factor('alpha191_169_45d', {})
class Factor_alpha191_169_45d(PublicFactor):
    name = 'alpha191_169_45d'
    description = 'SMA(MEAN(DELAY(SMA(C-DELAY(C,1),9,1),1),12)-MEAN(DELAY(SMA(C-DELAY(C,1),9,1),1),26),10,1)；原目录：GTJA_Alpha191_169；追踪：PF00263；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
