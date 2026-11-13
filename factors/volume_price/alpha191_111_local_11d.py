"""国泰君安 Alpha191

公式：SMA(V*((C-L)-(H-C))/(H-L),11,2)-SMA(V*((C-L)-(H-C))/(H-L),4,2)；原目录：GTJA_Alpha191_111；追踪：PF00207；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_111_local_11d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '-', ['call', 'sma', [['bin', '/', ['bin', '*', ['var', 'V'], ['bin', '-', ['bin', '-', ['var', 'C'], ['var', 'L']], ['bin', '-', ['var', 'H'], ['var', 'C']]]], ['bin', '-', ['var', 'H'], ['var', 'L']]], ['num', 11.0], ['num', 2.0]]], ['call', 'sma', [['bin', '/', ['bin', '*', ['var', 'V'], ['bin', '-', ['bin', '-', ['var', 'C'], ['var', 'L']], ['bin', '-', ['var', 'H'], ['var', 'C']]]], ['bin', '-', ['var', 'H'], ['var', 'L']]], ['num', 4.0], ['num', 2.0]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_111_local_11d', {})
class Factor_alpha191_111_local_11d(PublicFactor):
    name = 'alpha191_111_local_11d'
    description = 'SMA(V*((C-L)-(H-C))/(H-L),11,2)-SMA(V*((C-L)-(H-C))/(H-L),4,2)；原目录：GTJA_Alpha191_111；追踪：PF00207；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
