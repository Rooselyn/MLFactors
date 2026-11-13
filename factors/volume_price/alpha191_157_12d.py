"""国泰君安 Alpha191

公式：(MIN(PROD(RANK(RANK(LOG(SUM(TSMIN(RANK(RANK((-1*RANK(DELTA((C-1),5))))),2),1)))),1),5)+TSRANK(DELAY((-1*R),6),5))；原目录：GTJA_Alpha191_157；追踪：PF00251；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_157_12d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '+', ['call', 'min', [['call', 'prod', [['call', 'rank', [['call', 'rank', [['call', 'log', [['call', 'sum', [['call', 'tsmin', [['call', 'rank', [['call', 'rank', [['bin', '*', ['unary', '-', ['num', 1.0]], ['call', 'rank', [['call', 'delta', [['bin', '-', ['var', 'C'], ['num', 1.0]], ['num', 5.0]]]]]]]]]], ['num', 2.0]]], ['num', 1.0]]]]]]]]], ['num', 1.0]]], ['num', 5.0]]], ['call', 'tsrank', [['call', 'delay', [['bin', '*', ['unary', '-', ['num', 1.0]], ['var', 'R']], ['num', 6.0]]], ['num', 5.0]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_157_12d', {})
class Factor_alpha191_157_12d(PublicFactor):
    name = 'alpha191_157_12d'
    description = '(MIN(PROD(RANK(RANK(LOG(SUM(TSMIN(RANK(RANK((-1*RANK(DELTA((C-1),5))))),2),1)))),1),5)+TSRANK(DELAY((-1*R),6),5))；原目录：GTJA_Alpha191_157；追踪：PF00251；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
