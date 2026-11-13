"""国泰君安 Alpha191

公式：SMA(((C-MEAN(C,6))/MEAN(C,6)-DELAY((C-MEAN(C,6))/MEAN(C,6),3)),12,1)；原目录：GTJA_Alpha191_022；追踪：PF00122；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_022_local_20d', 'engine': 'alpha', 'kind': 191, 'tree': ['call', 'sma', [['bin', '-', ['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'mean', [['var', 'C'], ['num', 6.0]]]], ['call', 'mean', [['var', 'C'], ['num', 6.0]]]], ['call', 'delay', [['bin', '/', ['bin', '-', ['var', 'C'], ['call', 'mean', [['var', 'C'], ['num', 6.0]]]], ['call', 'mean', [['var', 'C'], ['num', 6.0]]]], ['num', 3.0]]]], ['num', 12.0], ['num', 1.0]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_022_local_20d', {})
class Factor_alpha191_022_local_20d(PublicFactor):
    name = 'alpha191_022_local_20d'
    description = 'SMA(((C-MEAN(C,6))/MEAN(C,6)-DELAY((C-MEAN(C,6))/MEAN(C,6),3)),12,1)；原目录：GTJA_Alpha191_022；追踪：PF00122；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
