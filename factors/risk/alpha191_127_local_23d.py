"""国泰君安 Alpha191

公式：MEAN((100*(C-MAX(C,12))/MAX(C,12))^2,12)^(1/2)；原目录：GTJA_Alpha191_127；追踪：PF00221；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_127_local_23d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '^', ['call', 'mean', [['bin', '^', ['bin', '/', ['bin', '*', ['num', 100.0], ['bin', '-', ['var', 'C'], ['call', 'max', [['var', 'C'], ['num', 12.0]]]]], ['call', 'max', [['var', 'C'], ['num', 12.0]]]], ['num', 2.0]], ['num', 12.0]]], ['bin', '/', ['num', 1.0], ['num', 2.0]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_127_local_23d', {})
class Factor_alpha191_127_local_23d(PublicFactor):
    name = 'alpha191_127_local_23d'
    description = 'MEAN((100*(C-MAX(C,12))/MAX(C,12))^2,12)^(1/2)；原目录：GTJA_Alpha191_127；追踪：PF00221；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
