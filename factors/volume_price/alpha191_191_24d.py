"""国泰君安 Alpha191

公式：((CORR(MEAN(V,20),L,5)+((H+L)/2))-C)；原目录：GTJA_Alpha191_191；追踪：PF00285；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_191_24d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '-', ('bin', '+', ('call', 'corr', [('call', 'mean', [('var', 'V'), ('num', 20.0)]), ('var', 'L'), ('num', 5.0)]), ('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0))), ('var', 'C'))}

@register_factor
@fixed_factor('alpha191_191_24d', {})
class Factor_alpha191_191_24d(PublicFactor):
    name = 'alpha191_191_24d'
    description = '((CORR(MEAN(V,20),L,5)+((H+L)/2))-C)；原目录：GTJA_Alpha191_191；追踪：PF00285；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
