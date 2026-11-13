"""国泰君安 Alpha191

公式：((RANK((C-MAX(C,5)))*RANK(CORR((MEAN(V,40)),L,5)))*-1)；原目录：GTJA_Alpha191_091；追踪：PF00188；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_091_44d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '*', ['bin', '*', ['call', 'rank', [['bin', '-', ['var', 'C'], ['call', 'max', [['var', 'C'], ['num', 5.0]]]]]], ['call', 'rank', [['call', 'corr', [['call', 'mean', [['var', 'V'], ['num', 40.0]]], ['var', 'L'], ['num', 5.0]]]]]], ['unary', '-', ['num', 1.0]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_091_44d', {})
class Factor_alpha191_091_44d(PublicFactor):
    name = 'alpha191_091_44d'
    description = '((RANK((C-MAX(C,5)))*RANK(CORR((MEAN(V,40)),L,5)))*-1)；原目录：GTJA_Alpha191_091；追踪：PF00188；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
