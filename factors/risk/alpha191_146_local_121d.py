"""国泰君安 Alpha191

公式：MEAN((C-DELAY(C,1))/DELAY(C,1)-SMA((C-DELAY(C,1))/DELAY(C,1),61,2),20)*((C-DELAY(C,1))/DELAY(C,1)-SMA((C-DELAY(C,1))/DELAY(C,1),61,2))/SMA(((C-DELAY(C,1))/DELAY(C,1)-((C-DELAY(C,1))/DELAY(C,1)-SMA((C-DELAY(C,1))/DELAY(C,1),61,2)))^2,60,1);；原目录：GTJA_Alpha191_146；追踪：PF00240；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_146_local_121d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '/', ['bin', '*', ['call', 'mean', [['bin', '-', ['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['call', 'sma', [['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 61.0], ['num', 2.0]]]], ['num', 20.0]]], ['bin', '-', ['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['call', 'sma', [['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 61.0], ['num', 2.0]]]]], ['call', 'sma', [['bin', '^', ['bin', '-', ['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['bin', '-', ['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['call', 'sma', [['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 61.0], ['num', 2.0]]]]], ['num', 2.0]], ['num', 60.0], ['num', 1.0]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_146_local_121d', {})
class Factor_alpha191_146_local_121d(PublicFactor):
    name = 'alpha191_146_local_121d'
    description = 'MEAN((C-DELAY(C,1))/DELAY(C,1)-SMA((C-DELAY(C,1))/DELAY(C,1),61,2),20)*((C-DELAY(C,1))/DELAY(C,1)-SMA((C-DELAY(C,1))/DELAY(C,1),61,2))/SMA(((C-DELAY(C,1))/DELAY(C,1)-((C-DELAY(C,1))/DELAY(C,1)-SMA((C-DELAY(C,1))/DELAY(C,1),61,2)))^2,60,1);；原目录：GTJA_Alpha191_146；追踪：PF00240；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
