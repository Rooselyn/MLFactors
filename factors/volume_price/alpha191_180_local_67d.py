"""国泰君安 Alpha191

公式：(MEAN(V,20)<V)?(-TSRANK(ABS(DELTA(C,7)),60)*SIGN(DELTA(C,7))):(-V)；原目录：GTJA_Alpha191_180；追踪：PF00274；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_180_local_67d', 'engine': 'alpha', 'kind': 191, 'tree': ['if', ['bin', '<', ['call', 'mean', [['var', 'V'], ['num', 20.0]]], ['var', 'V']], ['bin', '*', ['unary', '-', ['call', 'tsrank', [['call', 'abs', [['call', 'delta', [['var', 'C'], ['num', 7.0]]]]], ['num', 60.0]]]], ['call', 'sign', [['call', 'delta', [['var', 'C'], ['num', 7.0]]]]]], ['unary', '-', ['var', 'V']]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_180_local_67d', {})
class Factor_alpha191_180_local_67d(PublicFactor):
    name = 'alpha191_180_local_67d'
    description = '(MEAN(V,20)<V)?(-TSRANK(ABS(DELTA(C,7)),60)*SIGN(DELTA(C,7))):(-V)；原目录：GTJA_Alpha191_180；追踪：PF00274；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
