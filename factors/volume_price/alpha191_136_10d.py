"""国泰君安 Alpha191

公式：((-1*RANK(DELTA(R,3)))*CORR(O,V,10))；原目录：GTJA_Alpha191_136；追踪：PF00230；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_136_10d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('call', 'delta', [('var', 'R'), ('num', 3.0)])])), ('call', 'corr', [('var', 'O'), ('var', 'V'), ('num', 10.0)]))}

@register_factor
@fixed_factor('alpha191_136_10d', {})
class Factor_alpha191_136_10d(PublicFactor):
    name = 'alpha191_136_10d'
    description = '((-1*RANK(DELTA(R,3)))*CORR(O,V,10))；原目录：GTJA_Alpha191_136；追踪：PF00230；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
