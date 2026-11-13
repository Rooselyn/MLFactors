"""国泰君安 Alpha191

公式：(C-DELAY(C,12))/DELAY(C,12)*V；原目录：GTJA_Alpha191_134；追踪：PF00228；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_134_13d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '/', ('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 12.0)])), ('call', 'delay', [('var', 'C'), ('num', 12.0)])), ('var', 'V'))}

@register_factor
@fixed_factor('alpha191_134_13d', {})
class Factor_alpha191_134_13d(PublicFactor):
    name = 'alpha191_134_13d'
    description = '(C-DELAY(C,12))/DELAY(C,12)*V；原目录：GTJA_Alpha191_134；追踪：PF00228；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
