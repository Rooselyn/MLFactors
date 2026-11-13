"""国泰君安 Alpha191

公式：(-1*TSMAX(RANK(CORR(RANK(V),RANK(P),5)),5))；原目录：GTJA_Alpha191_016；追踪：PF00116；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_016_9d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'tsmax', [('call', 'rank', [('call', 'corr', [('call', 'rank', [('var', 'V')]), ('call', 'rank', [('var', 'P')]), ('num', 5.0)])]), ('num', 5.0)]))}

@register_factor
@fixed_factor('alpha191_016_9d', {})
class Factor_alpha191_016_9d(PublicFactor):
    name = 'alpha191_016_9d'
    description = '(-1*TSMAX(RANK(CORR(RANK(V),RANK(P),5)),5))；原目录：GTJA_Alpha191_016；追踪：PF00116；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
