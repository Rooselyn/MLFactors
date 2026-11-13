"""国泰君安 Alpha191

公式：100-(100/(1+SUM(((H+L+C)/3>DELAY((H+L+C)/3,1)?(H+L+C)/3*V:0),14)/SUM(((H+L+C)/3<DELAY((H+L+C)/3,1)?(H+L+C)/3*V:0),14)))；原目录：GTJA_Alpha191_128；追踪：PF00222；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_128_15d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '-', ('num', 100.0), ('bin', '/', ('num', 100.0), ('bin', '+', ('num', 1.0), ('bin', '/', ('call', 'sum', [('if', ('bin', '>', ('bin', '/', ('bin', '+', ('bin', '+', ('var', 'H'), ('var', 'L')), ('var', 'C')), ('num', 3.0)), ('call', 'delay', [('bin', '/', ('bin', '+', ('bin', '+', ('var', 'H'), ('var', 'L')), ('var', 'C')), ('num', 3.0)), ('num', 1.0)])), ('bin', '*', ('bin', '/', ('bin', '+', ('bin', '+', ('var', 'H'), ('var', 'L')), ('var', 'C')), ('num', 3.0)), ('var', 'V')), ('num', 0.0)), ('num', 14.0)]), ('call', 'sum', [('if', ('bin', '<', ('bin', '/', ('bin', '+', ('bin', '+', ('var', 'H'), ('var', 'L')), ('var', 'C')), ('num', 3.0)), ('call', 'delay', [('bin', '/', ('bin', '+', ('bin', '+', ('var', 'H'), ('var', 'L')), ('var', 'C')), ('num', 3.0)), ('num', 1.0)])), ('bin', '*', ('bin', '/', ('bin', '+', ('bin', '+', ('var', 'H'), ('var', 'L')), ('var', 'C')), ('num', 3.0)), ('var', 'V')), ('num', 0.0)), ('num', 14.0)])))))}

@register_factor
@fixed_factor('alpha191_128_15d', {})
class Factor_alpha191_128_15d(PublicFactor):
    name = 'alpha191_128_15d'
    description = '100-(100/(1+SUM(((H+L+C)/3>DELAY((H+L+C)/3,1)?(H+L+C)/3*V:0),14)/SUM(((H+L+C)/3<DELAY((H+L+C)/3,1)?(H+L+C)/3*V:0),14)))；原目录：GTJA_Alpha191_128；追踪：PF00222；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
