"""国泰君安 Alpha191

公式：(MAX(RANK(DECAYLINEAR(CORR(RANK(P),RANK(V),4),4)),RANK(DECAYLINEAR(MAX(CORR(RANK(C),RANK(MEAN(V,60)),4),13),14)))*-1)；原目录：GTJA_Alpha191_064；追踪：PF00162；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_064_88d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '*', ['call', 'max', [['call', 'rank', [['call', 'decaylinear', [['call', 'corr', [['call', 'rank', [['var', 'P']]], ['call', 'rank', [['var', 'V']]], ['num', 4.0]]], ['num', 4.0]]]]], ['call', 'rank', [['call', 'decaylinear', [['call', 'max', [['call', 'corr', [['call', 'rank', [['var', 'C']]], ['call', 'rank', [['call', 'mean', [['var', 'V'], ['num', 60.0]]]]], ['num', 4.0]]], ['num', 13.0]]], ['num', 14.0]]]]]]], ['unary', '-', ['num', 1.0]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_064_88d', {})
class Factor_alpha191_064_88d(PublicFactor):
    name = 'alpha191_064_88d'
    description = '(MAX(RANK(DECAYLINEAR(CORR(RANK(P),RANK(V),4),4)),RANK(DECAYLINEAR(MAX(CORR(RANK(C),RANK(MEAN(V,60)),4),13),14)))*-1)；原目录：GTJA_Alpha191_064；追踪：PF00162；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
