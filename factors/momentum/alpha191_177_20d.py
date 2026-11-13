"""国泰君安 Alpha191

公式：((20-HIGHDAY(H,20))/20)*100；原目录：GTJA_Alpha191_177；追踪：PF00271；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
}
SPEC = {'name': 'alpha191_177_20d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '/', ('bin', '-', ('num', 20.0), ('call', 'highday', [('var', 'H'), ('num', 20.0)])), ('num', 20.0)), ('num', 100.0))}

@register_factor
@fixed_factor('alpha191_177_20d', {})
class Factor_alpha191_177_20d(PublicFactor):
    name = 'alpha191_177_20d'
    description = '((20-HIGHDAY(H,20))/20)*100；原目录：GTJA_Alpha191_177；追踪：PF00271；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
