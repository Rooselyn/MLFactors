"""国泰君安 Alpha191

公式：SMA((TSMAX(H,6)-C)/(TSMAX(H,6)-TSMIN(L,6))*100,15,1)；原目录：GTJA_Alpha191_072；追踪：PF00170；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_072_20d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'sma', [('bin', '*', ('bin', '/', ('bin', '-', ('call', 'tsmax', [('var', 'H'), ('num', 6.0)]), ('var', 'C')), ('bin', '-', ('call', 'tsmax', [('var', 'H'), ('num', 6.0)]), ('call', 'tsmin', [('var', 'L'), ('num', 6.0)]))), ('num', 100.0)), ('num', 15.0), ('num', 1.0)])}

@register_factor
@fixed_factor('alpha191_072_20d', {})
class Factor_alpha191_072_20d(PublicFactor):
    name = 'alpha191_072_20d'
    description = 'SMA((TSMAX(H,6)-C)/(TSMAX(H,6)-TSMIN(L,6))*100,15,1)；原目录：GTJA_Alpha191_072；追踪：PF00170；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
