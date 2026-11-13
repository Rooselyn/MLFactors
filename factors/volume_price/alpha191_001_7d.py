"""国泰君安 Alpha191

公式：(-1*CORR(RANK(DELTA(LOG(V),1)),RANK(((C-O)/O)),6))；原目录：GTJA_Alpha191_001；追踪：PF00102；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_001_7d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'corr', [('call', 'rank', [('call', 'delta', [('call', 'log', [('var', 'V')]), ('num', 1.0)])]), ('call', 'rank', [('bin', '/', ('bin', '-', ('var', 'C'), ('var', 'O')), ('var', 'O'))]), ('num', 6.0)]))}

@register_factor
@fixed_factor('alpha191_001_7d', {})
class Factor_alpha191_001_7d(PublicFactor):
    name = 'alpha191_001_7d'
    description = '(-1*CORR(RANK(DELTA(LOG(V),1)),RANK(((C-O)/O)),6))；原目录：GTJA_Alpha191_001；追踪：PF00102；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
