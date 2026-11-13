"""国泰君安 Alpha191

公式：REGBETA(MEAN(C,6),SEQUENCE(6),6)；原目录：GTJA_Alpha191_021；追踪：PF00121；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_021_local_11d', 'engine': 'alpha', 'kind': 191, 'tree': ['call', 'regbeta', [['call', 'mean', [['var', 'C'], ['num', 6.0]]], ['call', 'sequence', [['num', 6.0]]], ['num', 6.0]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_021_local_11d', {})
class Factor_alpha191_021_local_11d(PublicFactor):
    name = 'alpha191_021_local_11d'
    description = 'REGBETA(MEAN(C,6),SEQUENCE(6),6)；原目录：GTJA_Alpha191_021；追踪：PF00121；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
