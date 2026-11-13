"""国泰君安 Alpha191

公式：((((SUM(C,8)/8)+STD(C,8))<(SUM(C,2)/2))?(-1*1):(((SUM(C,2)/2)<((SUM(C,8)/8)-STD(C,8)))?1:(((1<(V/MEAN(V,20)))||((V/MEAN(V,20))==1))?1:(-1*1))))；原目录：GTJA_Alpha191_004；追踪：PF00105；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_004_20d', 'engine': 'alpha', 'kind': 191, 'tree': ('if', ('bin', '<', ('bin', '+', ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 8.0)]), ('num', 8.0)), ('call', 'std', [('var', 'C'), ('num', 8.0)])), ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 2.0)]), ('num', 2.0))), ('bin', '*', ('unary', '-', ('num', 1.0)), ('num', 1.0)), ('if', ('bin', '<', ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 2.0)]), ('num', 2.0)), ('bin', '-', ('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 8.0)]), ('num', 8.0)), ('call', 'std', [('var', 'C'), ('num', 8.0)]))), ('num', 1.0), ('if', ('bin', '||', ('bin', '<', ('num', 1.0), ('bin', '/', ('var', 'V'), ('call', 'mean', [('var', 'V'), ('num', 20.0)]))), ('bin', '==', ('bin', '/', ('var', 'V'), ('call', 'mean', [('var', 'V'), ('num', 20.0)])), ('num', 1.0))), ('num', 1.0), ('bin', '*', ('unary', '-', ('num', 1.0)), ('num', 1.0)))))}

@register_factor
@fixed_factor('alpha191_004_20d', {})
class Factor_alpha191_004_20d(PublicFactor):
    name = 'alpha191_004_20d'
    description = '((((SUM(C,8)/8)+STD(C,8))<(SUM(C,2)/2))?(-1*1):(((SUM(C,2)/2)<((SUM(C,8)/8)-STD(C,8)))?1:(((1<(V/MEAN(V,20)))||((V/MEAN(V,20))==1))?1:(-1*1))))；原目录：GTJA_Alpha191_004；追踪：PF00105；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
