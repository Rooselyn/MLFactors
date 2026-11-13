"""国泰君安 Alpha191

公式：SUM(MAX(0,H-DELAY((H+L+C)/3,1)),26)/SUM(MAX(0,DELAY((H+L+C)/3,1)-L),26)*100；原目录：GTJA_Alpha191_052；追踪：PF00150；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'alpha191_052_27d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '/', ('call', 'sum', [('call', 'max', [('num', 0.0), ('bin', '-', ('var', 'H'), ('call', 'delay', [('bin', '/', ('bin', '+', ('bin', '+', ('var', 'H'), ('var', 'L')), ('var', 'C')), ('num', 3.0)), ('num', 1.0)]))]), ('num', 26.0)]), ('call', 'sum', [('call', 'max', [('num', 0.0), ('bin', '-', ('call', 'delay', [('bin', '/', ('bin', '+', ('bin', '+', ('var', 'H'), ('var', 'L')), ('var', 'C')), ('num', 3.0)), ('num', 1.0)]), ('var', 'L'))]), ('num', 26.0)])), ('num', 100.0))}

@register_factor
@fixed_factor('alpha191_052_27d', {})
class Factor_alpha191_052_27d(PublicFactor):
    name = 'alpha191_052_27d'
    description = 'SUM(MAX(0,H-DELAY((H+L+C)/3,1)),26)/SUM(MAX(0,DELAY((H+L+C)/3,1)-L),26)*100；原目录：GTJA_Alpha191_052；追踪：PF00150；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
