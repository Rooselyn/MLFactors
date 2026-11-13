"""国泰君安 Alpha191

公式：MEAN(MAX(MAX((H-L),ABS(DELAY(C,1)-H)),ABS(DELAY(C,1)-L)),12)；原目录：GTJA_Alpha191_161；追踪：PF00255；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_161_13d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'mean', [('call', 'max', [('call', 'max', [('bin', '-', ('var', 'H'), ('var', 'L')), ('call', 'abs', [('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 1.0)]), ('var', 'H'))])]), ('call', 'abs', [('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 1.0)]), ('var', 'L'))])]), ('num', 12.0)])}

@register_factor
@fixed_factor('alpha191_161_13d', {})
class Factor_alpha191_161_13d(PublicFactor):
    name = 'alpha191_161_13d'
    description = 'MEAN(MAX(MAX((H-L),ABS(DELAY(C,1)-H)),ABS(DELAY(C,1)-L)),12)；原目录：GTJA_Alpha191_161；追踪：PF00255；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
