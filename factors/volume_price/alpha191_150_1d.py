"""国泰君安 Alpha191

公式：(C+H+L)/3*V；原目录：GTJA_Alpha191_150；追踪：PF00244；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_150_1d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '/', ('bin', '+', ('bin', '+', ('var', 'C'), ('var', 'H')), ('var', 'L')), ('num', 3.0)), ('var', 'V'))}

@register_factor
@fixed_factor('alpha191_150_1d', {})
class Factor_alpha191_150_1d(PublicFactor):
    name = 'alpha191_150_1d'
    description = '(C+H+L)/3*V；原目录：GTJA_Alpha191_150；追踪：PF00244；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
