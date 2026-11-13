"""国泰君安 Alpha191

公式：SMA((((C>DELAY(C,1))?1/(C-DELAY(C,1)):1)-MIN(((C>DELAY(C,1))?1/(C-DELAY(C,1)):1),12))/(H-L)*100,13,2)；原目录：GTJA_Alpha191_164；追踪：PF00258；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'alpha191_164_25d', 'engine': 'alpha', 'kind': 191, 'tree': ['call', 'sma', [['bin', '*', ['bin', '/', ['bin', '-', ['if', ['bin', '>', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['bin', '/', ['num', 1.0], ['bin', '-', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]], ['num', 1.0]], ['call', 'min', [['if', ['bin', '>', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['bin', '/', ['num', 1.0], ['bin', '-', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]], ['num', 1.0]], ['num', 12.0]]]], ['bin', '-', ['var', 'H'], ['var', 'L']]], ['num', 100.0]], ['num', 13.0], ['num', 2.0]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_164_25d', {})
class Factor_alpha191_164_25d(PublicFactor):
    name = 'alpha191_164_25d'
    description = 'SMA((((C>DELAY(C,1))?1/(C-DELAY(C,1)):1)-MIN(((C>DELAY(C,1))?1/(C-DELAY(C,1)):1),12))/(H-L)*100,13,2)；原目录：GTJA_Alpha191_164；追踪：PF00258；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
