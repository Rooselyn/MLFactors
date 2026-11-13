"""国泰君安 Alpha191

公式：((H-L–SMA(H-L,11,2))/SMA(H-L,11,2))*100；原目录：GTJA_Alpha191_188；追踪：PF00282；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'alpha191_188_11d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '/', ('bin', '-', ('bin', '-', ('var', 'H'), ('var', 'L')), ('call', 'sma', [('bin', '-', ('var', 'H'), ('var', 'L')), ('num', 11.0), ('num', 2.0)])), ('call', 'sma', [('bin', '-', ('var', 'H'), ('var', 'L')), ('num', 11.0), ('num', 2.0)])), ('num', 100.0))}

@register_factor
@fixed_factor('alpha191_188_11d', {})
class Factor_alpha191_188_11d(PublicFactor):
    name = 'alpha191_188_11d'
    description = '((H-L–SMA(H-L,11,2))/SMA(H-L,11,2))*100；原目录：GTJA_Alpha191_188；追踪：PF00282；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
