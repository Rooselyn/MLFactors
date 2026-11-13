"""国泰君安 Alpha191

公式：SMA(H-L,10,2)/SMA(SMA(H-L,10,2),10,2)；原目录：GTJA_Alpha191_109；追踪：PF00205；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'alpha191_109_19d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '/', ('call', 'sma', [('bin', '-', ('var', 'H'), ('var', 'L')), ('num', 10.0), ('num', 2.0)]), ('call', 'sma', [('call', 'sma', [('bin', '-', ('var', 'H'), ('var', 'L')), ('num', 10.0), ('num', 2.0)]), ('num', 10.0), ('num', 2.0)]))}

@register_factor
@fixed_factor('alpha191_109_19d', {})
class Factor_alpha191_109_19d(PublicFactor):
    name = 'alpha191_109_19d'
    description = 'SMA(H-L,10,2)/SMA(SMA(H-L,10,2),10,2)；原目录：GTJA_Alpha191_109；追踪：PF00205；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
