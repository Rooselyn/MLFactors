"""国泰君安 Alpha191

公式：(C-P)/DECAYLINEAR(RANK(TSMAX(C,30)),2)；原目录：GTJA_Alpha191_124；追踪：PF00218；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_124_31d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '/', ('bin', '-', ('var', 'C'), ('var', 'P')), ('call', 'decaylinear', [('call', 'rank', [('call', 'tsmax', [('var', 'C'), ('num', 30.0)])]), ('num', 2.0)]))}

@register_factor
@fixed_factor('alpha191_124_31d', {})
class Factor_alpha191_124_31d(PublicFactor):
    name = 'alpha191_124_31d'
    description = '(C-P)/DECAYLINEAR(RANK(TSMAX(C,30)),2)；原目录：GTJA_Alpha191_124；追踪：PF00218；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
