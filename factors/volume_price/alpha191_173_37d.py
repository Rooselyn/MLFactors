"""国泰君安 Alpha191

公式：3*SMA(C,13,2)-2*SMA(SMA(C,13,2),13,2)+SMA(SMA(SMA(LOG(C),13,2),13,2),13,2);；原目录：GTJA_Alpha191_173；追踪：PF00267；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_173_37d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '+', ('bin', '-', ('bin', '*', ('num', 3.0), ('call', 'sma', [('var', 'C'), ('num', 13.0), ('num', 2.0)])), ('bin', '*', ('num', 2.0), ('call', 'sma', [('call', 'sma', [('var', 'C'), ('num', 13.0), ('num', 2.0)]), ('num', 13.0), ('num', 2.0)]))), ('call', 'sma', [('call', 'sma', [('call', 'sma', [('call', 'log', [('var', 'C')]), ('num', 13.0), ('num', 2.0)]), ('num', 13.0), ('num', 2.0)]), ('num', 13.0), ('num', 2.0)]))}

@register_factor
@fixed_factor('alpha191_173_37d', {})
class Factor_alpha191_173_37d(PublicFactor):
    name = 'alpha191_173_37d'
    description = '3*SMA(C,13,2)-2*SMA(SMA(C,13,2),13,2)+SMA(SMA(SMA(LOG(C),13,2),13,2),13,2);；原目录：GTJA_Alpha191_173；追踪：PF00267；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
