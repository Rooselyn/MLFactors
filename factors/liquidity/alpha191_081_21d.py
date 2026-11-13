"""国泰君安 Alpha191

公式：SMA(V,21,2)；原目录：GTJA_Alpha191_081；追踪：PF00179；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_081_21d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'sma', [('var', 'V'), ('num', 21.0), ('num', 2.0)])}

@register_factor
@fixed_factor('alpha191_081_21d', {})
class Factor_alpha191_081_21d(PublicFactor):
    name = 'alpha191_081_21d'
    description = 'SMA(V,21,2)；原目录：GTJA_Alpha191_081；追踪：PF00179；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
