"""国泰君安 Alpha191

公式：SUM((C=DELAY(C,1)?0:C-(C>DELAY(C,1)?MIN(L,DELAY(C,1)):MAX(H,DELAY(C,1)))),20)；原目录：GTJA_Alpha191_059；追踪：PF00157；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'alpha191_059_21d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'sum', [('if', ('bin', '==', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 1.0)])), ('num', 0.0), ('bin', '-', ('var', 'C'), ('if', ('bin', '>', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 1.0)])), ('call', 'min', [('var', 'L'), ('call', 'delay', [('var', 'C'), ('num', 1.0)])]), ('call', 'max', [('var', 'H'), ('call', 'delay', [('var', 'C'), ('num', 1.0)])])))), ('num', 20.0)])}

@register_factor
@fixed_factor('alpha191_059_21d', {})
class Factor_alpha191_059_21d(PublicFactor):
    name = 'alpha191_059_21d'
    description = 'SUM((C=DELAY(C,1)?0:C-(C>DELAY(C,1)?MIN(L,DELAY(C,1)):MAX(H,DELAY(C,1)))),20)；原目录：GTJA_Alpha191_059；追踪：PF00157；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
