"""国泰君安 Alpha191

公式：RANK((P-MAX(P,15)))^DELTA(C,5)；原目录：GTJA_Alpha191_017；追踪：PF00117；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_017_15d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '^', ['call', 'rank', [['bin', '-', ['var', 'P'], ['call', 'max', [['var', 'P'], ['num', 15.0]]]]]], ['call', 'delta', [['var', 'C'], ['num', 5.0]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_017_15d', {})
class Factor_alpha191_017_15d(PublicFactor):
    name = 'alpha191_017_15d'
    description = 'RANK((P-MAX(P,15)))^DELTA(C,5)；原目录：GTJA_Alpha191_017；追踪：PF00117；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
