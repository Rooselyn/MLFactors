"""国泰君安 Alpha191

公式：SMA(V,13,2)-SMA(V,27,2)-SMA(SMA(V,13,2)-SMA(V,27,2),10,2)；原目录：GTJA_Alpha191_155；追踪：PF00249；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_155_36d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '-', ('bin', '-', ('call', 'sma', [('var', 'V'), ('num', 13.0), ('num', 2.0)]), ('call', 'sma', [('var', 'V'), ('num', 27.0), ('num', 2.0)])), ('call', 'sma', [('bin', '-', ('call', 'sma', [('var', 'V'), ('num', 13.0), ('num', 2.0)]), ('call', 'sma', [('var', 'V'), ('num', 27.0), ('num', 2.0)])), ('num', 10.0), ('num', 2.0)]))}

@register_factor
@fixed_factor('alpha191_155_36d', {})
class Factor_alpha191_155_36d(PublicFactor):
    name = 'alpha191_155_36d'
    description = 'SMA(V,13,2)-SMA(V,27,2)-SMA(SMA(V,13,2)-SMA(V,27,2),10,2)；原目录：GTJA_Alpha191_155；追踪：PF00249；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
