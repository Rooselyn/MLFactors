"""国泰君安 Alpha191

公式：(RANK(SIGN(DELTA((((O*0.85)+(H*0.15))),4)))*-1)；原目录：GTJA_Alpha191_006；追踪：PF00107；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'alpha191_006_5d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('call', 'rank', [('call', 'sign', [('call', 'delta', [('bin', '+', ('bin', '*', ('var', 'O'), ('num', 0.85)), ('bin', '*', ('var', 'H'), ('num', 0.15))), ('num', 4.0)])])]), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_006_5d', {})
class Factor_alpha191_006_5d(PublicFactor):
    name = 'alpha191_006_5d'
    description = '(RANK(SIGN(DELTA((((O*0.85)+(H*0.15))),4)))*-1)；原目录：GTJA_Alpha191_006；追踪：PF00107；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
