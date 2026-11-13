"""国泰君安 Alpha191

公式：SMA(C-DELAY(C,5),5,1)；原目录：GTJA_Alpha191_024；追踪：PF00124；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_024_10d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'sma', [('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 5.0)])), ('num', 5.0), ('num', 1.0)])}

@register_factor
@fixed_factor('alpha191_024_10d', {})
class Factor_alpha191_024_10d(PublicFactor):
    name = 'alpha191_024_10d'
    description = 'SMA(C-DELAY(C,5),5,1)；原目录：GTJA_Alpha191_024；追踪：PF00124；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
