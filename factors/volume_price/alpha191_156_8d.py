"""国泰君安 Alpha191

公式：(MAX(RANK(DECAYLINEAR(DELTA(P,5),3)),RANK(DECAYLINEAR(((DELTA(((O*0.15)+(L*0.85)),2)/((O*0.15)+(L*0.85)))*-1),3)))*-1)；原目录：GTJA_Alpha191_156；追踪：PF00250；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_156_8d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('call', 'max', [('call', 'rank', [('call', 'decaylinear', [('call', 'delta', [('var', 'P'), ('num', 5.0)]), ('num', 3.0)])]), ('call', 'rank', [('call', 'decaylinear', [('bin', '*', ('bin', '/', ('call', 'delta', [('bin', '+', ('bin', '*', ('var', 'O'), ('num', 0.15)), ('bin', '*', ('var', 'L'), ('num', 0.85))), ('num', 2.0)]), ('bin', '+', ('bin', '*', ('var', 'O'), ('num', 0.15)), ('bin', '*', ('var', 'L'), ('num', 0.85)))), ('unary', '-', ('num', 1.0))), ('num', 3.0)])])]), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_156_8d', {})
class Factor_alpha191_156_8d(PublicFactor):
    name = 'alpha191_156_8d'
    description = '(MAX(RANK(DECAYLINEAR(DELTA(P,5),3)),RANK(DECAYLINEAR(((DELTA(((O*0.15)+(L*0.85)),2)/((O*0.15)+(L*0.85)))*-1),3)))*-1)；原目录：GTJA_Alpha191_156；追踪：PF00250；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
