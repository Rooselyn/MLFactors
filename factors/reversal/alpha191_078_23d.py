"""国泰君安 Alpha191

公式：((H+L+C)/3-MA((H+L+C)/3,12))/(0.015*MEAN(ABS(C-MEAN((H+L+C)/3,12)),12))；原目录：GTJA_Alpha191_078；追踪：PF00176；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_078_23d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '/', ['bin', '-', ['bin', '/', ['bin', '+', ['bin', '+', ['var', 'H'], ['var', 'L']], ['var', 'C']], ['num', 3.0]], ['call', 'ma', [['bin', '/', ['bin', '+', ['bin', '+', ['var', 'H'], ['var', 'L']], ['var', 'C']], ['num', 3.0]], ['num', 12.0]]]], ['bin', '*', ['num', 0.015], ['call', 'mean', [['call', 'abs', [['bin', '-', ['var', 'C'], ['call', 'mean', [['bin', '/', ['bin', '+', ['bin', '+', ['var', 'H'], ['var', 'L']], ['var', 'C']], ['num', 3.0]], ['num', 12.0]]]]]], ['num', 12.0]]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_078_23d', {})
class Factor_alpha191_078_23d(PublicFactor):
    name = 'alpha191_078_23d'
    description = '((H+L+C)/3-MA((H+L+C)/3,12))/(0.015*MEAN(ABS(C-MEAN((H+L+C)/3,12)),12))；原目录：GTJA_Alpha191_078；追踪：PF00176；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
