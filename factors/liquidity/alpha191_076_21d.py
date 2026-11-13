"""国泰君安 Alpha191

公式：STD(ABS((C/DELAY(C,1)-1))/V,20)/MEAN(ABS((C/DELAY(C,1)-1))/V,20)；原目录：GTJA_Alpha191_076；追踪：PF00174；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_076_21d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '/', ('call', 'std', [('bin', '/', ('call', 'abs', [('bin', '-', ('bin', '/', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 1.0)])), ('num', 1.0))]), ('var', 'V')), ('num', 20.0)]), ('call', 'mean', [('bin', '/', ('call', 'abs', [('bin', '-', ('bin', '/', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 1.0)])), ('num', 1.0))]), ('var', 'V')), ('num', 20.0)]))}

@register_factor
@fixed_factor('alpha191_076_21d', {})
class Factor_alpha191_076_21d(PublicFactor):
    name = 'alpha191_076_21d'
    description = 'STD(ABS((C/DELAY(C,1)-1))/V,20)/MEAN(ABS((C/DELAY(C,1)-1))/V,20)；原目录：GTJA_Alpha191_076；追踪：PF00174；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
