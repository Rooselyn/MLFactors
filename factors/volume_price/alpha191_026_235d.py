"""国泰君安 Alpha191

公式：((((SUM(C,7)/7)-C))+((CORR(P,DELAY(C,5),230))))；原目录：GTJA_Alpha191_026；追踪：PF00126；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_026_235d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '+', ('bin', '-', ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 7.0)]), ('num', 7.0)), ('var', 'C')), ('call', 'corr', [('var', 'P'), ('call', 'delay', [('var', 'C'), ('num', 5.0)]), ('num', 230.0)]))}

@register_factor
@fixed_factor('alpha191_026_235d', {})
class Factor_alpha191_026_235d(PublicFactor):
    name = 'alpha191_026_235d'
    description = '((((SUM(C,7)/7)-C))+((CORR(P,DELAY(C,5),230))))；原目录：GTJA_Alpha191_026；追踪：PF00126；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
