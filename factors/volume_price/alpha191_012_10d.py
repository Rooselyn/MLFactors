"""国泰君安 Alpha191

公式：(RANK((O-(SUM(P,10)/10))))*(-1*(RANK(ABS((C-P)))))；原目录：GTJA_Alpha191_012；追踪：PF00113；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_012_10d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('call', 'rank', [('bin', '-', ('var', 'O'), ('bin', '/', ('call', 'sum', [('var', 'P'), ('num', 10.0)]), ('num', 10.0)))]), ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'rank', [('call', 'abs', [('bin', '-', ('var', 'C'), ('var', 'P'))])])))}

@register_factor
@fixed_factor('alpha191_012_10d', {})
class Factor_alpha191_012_10d(PublicFactor):
    name = 'alpha191_012_10d'
    description = '(RANK((O-(SUM(P,10)/10))))*(-1*(RANK(ABS((C-P)))))；原目录：GTJA_Alpha191_012；追踪：PF00113；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
