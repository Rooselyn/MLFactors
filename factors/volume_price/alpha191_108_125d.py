"""国泰君安 Alpha191

公式：((RANK((H-MIN(H,2)))^RANK(CORR((P),(MEAN(V,120)),6)))*-1)；原目录：GTJA_Alpha191_108；追踪：PF00204；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_108_125d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '*', ['bin', '^', ['call', 'rank', [['bin', '-', ['var', 'H'], ['call', 'min', [['var', 'H'], ['num', 2.0]]]]]], ['call', 'rank', [['call', 'corr', [['var', 'P'], ['call', 'mean', [['var', 'V'], ['num', 120.0]]], ['num', 6.0]]]]]], ['unary', '-', ['num', 1.0]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_108_125d', {})
class Factor_alpha191_108_125d(PublicFactor):
    name = 'alpha191_108_125d'
    description = '((RANK((H-MIN(H,2)))^RANK(CORR((P),(MEAN(V,120)),6)))*-1)；原目录：GTJA_Alpha191_108；追踪：PF00204；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
