"""国泰君安 Alpha191

公式：SMA(((H+L)/2-(DELAY(H,1)+DELAY(L,1))/2)*(H-L)/V,15,2)；原目录：GTJA_Alpha191_068；追踪：PF00166；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_068_16d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'sma', [('bin', '/', ('bin', '*', ('bin', '-', ('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('bin', '/', ('bin', '+', ('call', 'delay', [('var', 'H'), ('num', 1.0)]), ('call', 'delay', [('var', 'L'), ('num', 1.0)])), ('num', 2.0))), ('bin', '-', ('var', 'H'), ('var', 'L'))), ('var', 'V')), ('num', 15.0), ('num', 2.0)])}

@register_factor
@fixed_factor('alpha191_068_16d', {})
class Factor_alpha191_068_16d(PublicFactor):
    name = 'alpha191_068_16d'
    description = 'SMA(((H+L)/2-(DELAY(H,1)+DELAY(L,1))/2)*(H-L)/V,15,2)；原目录：GTJA_Alpha191_068；追踪：PF00166；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
