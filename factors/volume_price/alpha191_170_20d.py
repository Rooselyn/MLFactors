"""国泰君安 Alpha191

公式：((((RANK((1/C))*V)/MEAN(V,20))*((H*RANK((H-C)))/(SUM(H,5)/5)))-RANK((P-DELAY(P,5))))；原目录：GTJA_Alpha191_170；追踪：PF00264；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_170_20d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '-', ('bin', '*', ('bin', '/', ('bin', '*', ('call', 'rank', [('bin', '/', ('num', 1.0), ('var', 'C'))]), ('var', 'V')), ('call', 'mean', [('var', 'V'), ('num', 20.0)])), ('bin', '/', ('bin', '*', ('var', 'H'), ('call', 'rank', [('bin', '-', ('var', 'H'), ('var', 'C'))])), ('bin', '/', ('call', 'sum', [('var', 'H'), ('num', 5.0)]), ('num', 5.0)))), ('call', 'rank', [('bin', '-', ('var', 'P'), ('call', 'delay', [('var', 'P'), ('num', 5.0)]))]))}

@register_factor
@fixed_factor('alpha191_170_20d', {})
class Factor_alpha191_170_20d(PublicFactor):
    name = 'alpha191_170_20d'
    description = '((((RANK((1/C))*V)/MEAN(V,20))*((H*RANK((H-C)))/(SUM(H,5)/5)))-RANK((P-DELAY(P,5))))；原目录：GTJA_Alpha191_170；追踪：PF00264；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
