"""国泰君安 Alpha191

公式：(-1*DELTA((((C-L)-(H-C))/(H-L)),1))；原目录：GTJA_Alpha191_002；追踪：PF00103；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_002_2d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'delta', [('bin', '/', ('bin', '-', ('bin', '-', ('var', 'C'), ('var', 'L')), ('bin', '-', ('var', 'H'), ('var', 'C'))), ('bin', '-', ('var', 'H'), ('var', 'L'))), ('num', 1.0)]))}

@register_factor
@fixed_factor('alpha191_002_2d', {})
class Factor_alpha191_002_2d(PublicFactor):
    name = 'alpha191_002_2d'
    description = '(-1*DELTA((((C-L)-(H-C))/(H-L)),1))；原目录：GTJA_Alpha191_002；追踪：PF00103；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
