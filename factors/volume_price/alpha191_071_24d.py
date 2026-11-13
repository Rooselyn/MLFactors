"""国泰君安 Alpha191

公式：(C-MEAN(C,24))/MEAN(C,24)*100；原目录：GTJA_Alpha191_071；追踪：PF00169；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_071_24d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '/', ('bin', '-', ('var', 'C'), ('call', 'mean', [('var', 'C'), ('num', 24.0)])), ('call', 'mean', [('var', 'C'), ('num', 24.0)])), ('num', 100.0))}

@register_factor
@fixed_factor('alpha191_071_24d', {})
class Factor_alpha191_071_24d(PublicFactor):
    name = 'alpha191_071_24d'
    description = '(C-MEAN(C,24))/MEAN(C,24)*100；原目录：GTJA_Alpha191_071；追踪：PF00169；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
