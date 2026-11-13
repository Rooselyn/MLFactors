"""国泰君安 Alpha191

公式：CORR(RANK(((C-TSMIN(L,12))/(TSMAX(H,12)-TSMIN(L,12)))),RANK(V),6)；原目录：GTJA_Alpha191_176；追踪：PF00270；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_176_17d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'corr', [('call', 'rank', [('bin', '/', ('bin', '-', ('var', 'C'), ('call', 'tsmin', [('var', 'L'), ('num', 12.0)])), ('bin', '-', ('call', 'tsmax', [('var', 'H'), ('num', 12.0)]), ('call', 'tsmin', [('var', 'L'), ('num', 12.0)])))]), ('call', 'rank', [('var', 'V')]), ('num', 6.0)])}

@register_factor
@fixed_factor('alpha191_176_17d', {})
class Factor_alpha191_176_17d(PublicFactor):
    name = 'alpha191_176_17d'
    description = 'CORR(RANK(((C-TSMIN(L,12))/(TSMAX(H,12)-TSMIN(L,12)))),RANK(V),6)；原目录：GTJA_Alpha191_176；追踪：PF00270；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
