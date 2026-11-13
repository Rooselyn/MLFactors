"""国泰君安 Alpha191

公式：RANK(MAX(((R<0)?STD(R,20):C)^2,5))；原目录：GTJA_Alpha191_010；追踪：PF00111；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_010_local_25d', 'engine': 'alpha', 'kind': 191, 'tree': ['call', 'rank', [['call', 'max', [['bin', '^', ['if', ['bin', '<', ['var', 'R'], ['num', 0.0]], ['call', 'std', [['var', 'R'], ['num', 20.0]]], ['var', 'C']], ['num', 2.0]], ['num', 5.0]]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_010_local_25d', {})
class Factor_alpha191_010_local_25d(PublicFactor):
    name = 'alpha191_010_local_25d'
    description = 'RANK(MAX(((R<0)?STD(R,20):C)^2,5))；原目录：GTJA_Alpha191_010；追踪：PF00111；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
