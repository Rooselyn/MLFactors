"""国泰君安 Alpha191

公式：((C-SUM(MIN(L,DELAY(C,1)),6))/SUM(MAX(H,DELAY(C,1))-MIN(L,DELAY(C,1)),6)*12*24+(C-SUM(MIN(L,DELAY(C,1)),12))/SUM(MAX(H,DELAY(C,1))-MIN(L,DELAY(C,1)),12)*6*24+(C-SUM(MIN(L,DELAY(C,1)),24))/SUM(MAX(H,DELAY(C,1))-MIN(L,DELAY(C,1)),24)*6*24)*100/(6*12+6*24+12*24)；原目录：GTJA_Alpha191_159；追踪：PF00253；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_159_local_25d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '/', ['bin', '*', ['bin', '+', ['bin', '+', ['bin', '*', ['bin', '*', ['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'sum', [['call', 'min', [['var', 'L'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]], ['num', 6.0]]]], ['call', 'sum', [['bin', '-', ['call', 'max', [['var', 'H'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]], ['call', 'min', [['var', 'L'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]]], ['num', 6.0]]]], ['num', 12.0]], ['num', 24.0]], ['bin', '*', ['bin', '*', ['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'sum', [['call', 'min', [['var', 'L'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]], ['num', 12.0]]]], ['call', 'sum', [['bin', '-', ['call', 'max', [['var', 'H'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]], ['call', 'min', [['var', 'L'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]]], ['num', 12.0]]]], ['num', 6.0]], ['num', 24.0]]], ['bin', '*', ['bin', '*', ['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'sum', [['call', 'min', [['var', 'L'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]], ['num', 24.0]]]], ['call', 'sum', [['bin', '-', ['call', 'max', [['var', 'H'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]], ['call', 'min', [['var', 'L'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]]]], ['num', 24.0]]]], ['num', 6.0]], ['num', 24.0]]], ['num', 100.0]], ['bin', '+', ['bin', '+', ['bin', '*', ['num', 6.0], ['num', 12.0]], ['bin', '*', ['num', 6.0], ['num', 24.0]]], ['bin', '*', ['num', 12.0], ['num', 24.0]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_159_local_25d', {})
class Factor_alpha191_159_local_25d(PublicFactor):
    name = 'alpha191_159_local_25d'
    description = '((C-SUM(MIN(L,DELAY(C,1)),6))/SUM(MAX(H,DELAY(C,1))-MIN(L,DELAY(C,1)),6)*12*24+(C-SUM(MIN(L,DELAY(C,1)),12))/SUM(MAX(H,DELAY(C,1))-MIN(L,DELAY(C,1)),12)*6*24+(C-SUM(MIN(L,DELAY(C,1)),24))/SUM(MAX(H,DELAY(C,1))-MIN(L,DELAY(C,1)),24)*6*24)*100/(6*12+6*24+12*24)；原目录：GTJA_Alpha191_159；追踪：PF00253；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
