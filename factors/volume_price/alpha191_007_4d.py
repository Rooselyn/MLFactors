"""国泰君安 Alpha191

公式：((RANK(MAX((P-C),3))+RANK(MIN((P-C),3)))*RANK(DELTA(V,3)))；原目录：GTJA_Alpha191_007；追踪：PF00108；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_007_4d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '*', ['bin', '+', ['call', 'rank', [['call', 'max', [['bin', '-', ['var', 'P'], ['var', 'C']], ['num', 3.0]]]]], ['call', 'rank', [['call', 'min', [['bin', '-', ['var', 'P'], ['var', 'C']], ['num', 3.0]]]]]], ['call', 'rank', [['call', 'delta', [['var', 'V'], ['num', 3.0]]]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_007_4d', {})
class Factor_alpha191_007_4d(PublicFactor):
    name = 'alpha191_007_4d'
    description = '((RANK(MAX((P-C),3))+RANK(MIN((P-C),3)))*RANK(DELTA(V,3)))；原目录：GTJA_Alpha191_007；追踪：PF00108；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
