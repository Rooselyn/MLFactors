"""国泰君安 Alpha191

公式：SUM(H-O,20)/SUM(O-L,20)*100；原目录：GTJA_Alpha191_118；追踪：PF00213；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'alpha191_118_20d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '/', ('call', 'sum', [('bin', '-', ('var', 'H'), ('var', 'O')), ('num', 20.0)]), ('call', 'sum', [('bin', '-', ('var', 'O'), ('var', 'L')), ('num', 20.0)])), ('num', 100.0))}

@register_factor
@fixed_factor('alpha191_118_20d', {})
class Factor_alpha191_118_20d(PublicFactor):
    name = 'alpha191_118_20d'
    description = 'SUM(H-O,20)/SUM(O-L,20)*100；原目录：GTJA_Alpha191_118；追踪：PF00213；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
