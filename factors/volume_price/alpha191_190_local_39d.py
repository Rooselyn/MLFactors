"""国泰君安 Alpha191

公式：LOG((COUNT((C/DELAY(C,1)-1)>((C/DELAY(C,19))^(1/20)-1),20)-1)*SUMIF(((C/DELAY(C,1)-1)-((C/DELAY(C,19))^(1/20)-1))^2,20,(C/DELAY(C,1)-1)<((C/DELAY(C,19))^(1/20)-1))/(COUNT((C/DELAY(C,1)-1)<((C/DELAY(C,19))^(1/20)-1),20)*SUMIF(((C/DELAY(C,1)-1)-((C/DELAY(C,19))^(1/20)-1))^2,20,(C/DELAY(C,1)-1)>((C/DELAY(C,19))^(1/20)-1))))；原目录：GTJA_Alpha191_190；追踪：PF00284；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_190_local_39d', 'engine': 'alpha', 'kind': 191, 'tree': ['call', 'log', [['bin', '/', ['bin', '*', ['bin', '-', ['call', 'count', [['bin', '>', ['bin', '-', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 1.0]], ['bin', '-', ['bin', '^', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 19.0]]]], ['bin', '/', ['num', 1.0], ['num', 20.0]]], ['num', 1.0]]], ['num', 20.0]]], ['num', 1.0]], ['call', 'sumif', [['bin', '^', ['bin', '-', ['bin', '-', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 1.0]], ['bin', '-', ['bin', '^', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 19.0]]]], ['bin', '/', ['num', 1.0], ['num', 20.0]]], ['num', 1.0]]], ['num', 2.0]], ['num', 20.0], ['bin', '<', ['bin', '-', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 1.0]], ['bin', '-', ['bin', '^', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 19.0]]]], ['bin', '/', ['num', 1.0], ['num', 20.0]]], ['num', 1.0]]]]]], ['bin', '*', ['call', 'count', [['bin', '<', ['bin', '-', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 1.0]], ['bin', '-', ['bin', '^', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 19.0]]]], ['bin', '/', ['num', 1.0], ['num', 20.0]]], ['num', 1.0]]], ['num', 20.0]]], ['call', 'sumif', [['bin', '^', ['bin', '-', ['bin', '-', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 1.0]], ['bin', '-', ['bin', '^', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 19.0]]]], ['bin', '/', ['num', 1.0], ['num', 20.0]]], ['num', 1.0]]], ['num', 2.0]], ['num', 20.0], ['bin', '>', ['bin', '-', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 1.0]], ['bin', '-', ['bin', '^', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 19.0]]]], ['bin', '/', ['num', 1.0], ['num', 20.0]]], ['num', 1.0]]]]]]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_190_local_39d', {})
class Factor_alpha191_190_local_39d(PublicFactor):
    name = 'alpha191_190_local_39d'
    description = 'LOG((COUNT((C/DELAY(C,1)-1)>((C/DELAY(C,19))^(1/20)-1),20)-1)*SUMIF(((C/DELAY(C,1)-1)-((C/DELAY(C,19))^(1/20)-1))^2,20,(C/DELAY(C,1)-1)<((C/DELAY(C,19))^(1/20)-1))/(COUNT((C/DELAY(C,1)-1)<((C/DELAY(C,19))^(1/20)-1),20)*SUMIF(((C/DELAY(C,1)-1)-((C/DELAY(C,19))^(1/20)-1))^2,20,(C/DELAY(C,1)-1)>((C/DELAY(C,19))^(1/20)-1))))；原目录：GTJA_Alpha191_190；追踪：PF00284；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
