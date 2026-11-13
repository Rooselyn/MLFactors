"""国泰君安 Alpha191

公式：3*SMA((C-TSMIN(L,9))/(TSMAX(H,9)-TSMIN(L,9))*100,3,1)-2*SMA(SMA((C-TSMIN(L,9))/(MAX(H,9)-TSMAX(L,9))*100,3,1),3,1)；原目录：GTJA_Alpha191_028；追踪：PF00128；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_028_13d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '-', ['bin', '*', ['num', 3.0], ['call', 'sma', [['bin', '*', ['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'tsmin', [['var', 'L'], ['num', 9.0]]]], ['bin', '-', ['call', 'tsmax', [['var', 'H'], ['num', 9.0]]], ['call', 'tsmin', [['var', 'L'], ['num', 9.0]]]]], ['num', 100.0]], ['num', 3.0], ['num', 1.0]]]], ['bin', '*', ['num', 2.0], ['call', 'sma', [['call', 'sma', [['bin', '*', ['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'tsmin', [['var', 'L'], ['num', 9.0]]]], ['bin', '-', ['call', 'max', [['var', 'H'], ['num', 9.0]]], ['call', 'tsmax', [['var', 'L'], ['num', 9.0]]]]], ['num', 100.0]], ['num', 3.0], ['num', 1.0]]], ['num', 3.0], ['num', 1.0]]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_028_13d', {})
class Factor_alpha191_028_13d(PublicFactor):
    name = 'alpha191_028_13d'
    description = '3*SMA((C-TSMIN(L,9))/(TSMAX(H,9)-TSMIN(L,9))*100,3,1)-2*SMA(SMA((C-TSMIN(L,9))/(MAX(H,9)-TSMAX(L,9))*100,3,1),3,1)；原目录：GTJA_Alpha191_028；追踪：PF00128；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
