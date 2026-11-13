"""国泰君安 Alpha191

公式：(RANK(DELTA(P,1))^TSRANK(CORR(C,MEAN(V,50),18),18))；原目录：GTJA_Alpha191_131；追踪：PF00225；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_131_local_84d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '^', ['call', 'rank', [['call', 'delta', [['var', 'P'], ['num', 1.0]]]]], ['call', 'tsrank', [['call', 'corr', [['var', 'C'], ['call', 'mean', [['var', 'V'], ['num', 50.0]]], ['num', 18.0]]], ['num', 18.0]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_131_local_84d', {})
class Factor_alpha191_131_local_84d(PublicFactor):
    name = 'alpha191_131_local_84d'
    description = '(RANK(DELTA(P,1))^TSRANK(CORR(C,MEAN(V,50),18),18))；原目录：GTJA_Alpha191_131；追踪：PF00225；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
