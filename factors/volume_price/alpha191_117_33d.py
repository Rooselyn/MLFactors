"""国泰君安 Alpha191

公式：((TSRANK(V,32)*(1-TSRANK(((C+H)-L),16)))*(1-TSRANK(R,32)))；原目录：GTJA_Alpha191_117；追踪：PF00212；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_117_33d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '*', ('call', 'tsrank', [('var', 'V'), ('num', 32.0)]), ('bin', '-', ('num', 1.0), ('call', 'tsrank', [('bin', '-', ('bin', '+', ('var', 'C'), ('var', 'H')), ('var', 'L')), ('num', 16.0)]))), ('bin', '-', ('num', 1.0), ('call', 'tsrank', [('var', 'R'), ('num', 32.0)])))}

@register_factor
@fixed_factor('alpha191_117_33d', {})
class Factor_alpha191_117_33d(PublicFactor):
    name = 'alpha191_117_33d'
    description = '((TSRANK(V,32)*(1-TSRANK(((C+H)-L),16)))*(1-TSRANK(R,32)))；原目录：GTJA_Alpha191_117；追踪：PF00212；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
