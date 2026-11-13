"""国泰君安 Alpha191

公式：((((-1*TSMIN(L,5))+DELAY(TSMIN(L,5),5))*RANK(((SUM(R,240)-SUM(R,20))/220)))*TSRANK(V,5))；原目录：GTJA_Alpha191_033；追踪：PF00133；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_033_241d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '*', ('bin', '+', ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'tsmin', [('var', 'L'), ('num', 5.0)])), ('call', 'delay', [('call', 'tsmin', [('var', 'L'), ('num', 5.0)]), ('num', 5.0)])), ('call', 'rank', [('bin', '/', ('bin', '-', ('call', 'sum', [('var', 'R'), ('num', 240.0)]), ('call', 'sum', [('var', 'R'), ('num', 20.0)])), ('num', 220.0))])), ('call', 'tsrank', [('var', 'V'), ('num', 5.0)]))}

@register_factor
@fixed_factor('alpha191_033_241d', {})
class Factor_alpha191_033_241d(PublicFactor):
    name = 'alpha191_033_241d'
    description = '((((-1*TSMIN(L,5))+DELAY(TSMIN(L,5),5))*RANK(((SUM(R,240)-SUM(R,20))/220)))*TSRANK(V,5))；原目录：GTJA_Alpha191_033；追踪：PF00133；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
