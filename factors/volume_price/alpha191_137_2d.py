"""国泰君安 Alpha191

公式：16*(C-DELAY(C,1)+(C-O)/2+DELAY(C,1)-DELAY(O,1))/((ABS(H-DELAY(C,1))>ABS(L-DELAY(C,1))&ABS(H-DELAY(C,1))>ABS(H-DELAY(L,1))?ABS(H-DELAY(C,1))+ABS(L-DELAY(C,1))/2+ABS(DELAY(C,1)-DELAY(O,1))/4:(ABS(L-DELAY(C,1))>ABS(H-DELAY(L,1))&ABS(L-DELAY(C,1))>ABS(H-DELAY(C,1))?ABS(L-DELAY(C,1))+ABS(H-DELAY(C,1))/2+ABS(DELAY(C,1)-DELAY(O,1))/4:ABS(H-DELAY(L,1))+ABS(DELAY(C,1)-DELAY(O,1))/4)))*MAX(ABS(H-DELAY(C,1)),ABS(L-DELAY(C,1)))；原目录：GTJA_Alpha191_137；追踪：PF00231；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'alpha191_137_2d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '/', ('bin', '*', ('num', 16.0), ('bin', '-', ('bin', '+', ('bin', '+', ('bin', '-', ('var', 'C'), ('call', 'delay', [('var', 'C'), ('num', 1.0)])), ('bin', '/', ('bin', '-', ('var', 'C'), ('var', 'O')), ('num', 2.0))), ('call', 'delay', [('var', 'C'), ('num', 1.0)])), ('call', 'delay', [('var', 'O'), ('num', 1.0)]))), ('if', ('bin', '&&', ('bin', '>', ('call', 'abs', [('bin', '-', ('var', 'H'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('call', 'abs', [('bin', '-', ('var', 'L'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))])), ('bin', '>', ('call', 'abs', [('bin', '-', ('var', 'H'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('call', 'abs', [('bin', '-', ('var', 'H'), ('call', 'delay', [('var', 'L'), ('num', 1.0)]))]))), ('bin', '+', ('bin', '+', ('call', 'abs', [('bin', '-', ('var', 'H'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('bin', '/', ('call', 'abs', [('bin', '-', ('var', 'L'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('num', 2.0))), ('bin', '/', ('call', 'abs', [('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 1.0)]), ('call', 'delay', [('var', 'O'), ('num', 1.0)]))]), ('num', 4.0))), ('if', ('bin', '&&', ('bin', '>', ('call', 'abs', [('bin', '-', ('var', 'L'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('call', 'abs', [('bin', '-', ('var', 'H'), ('call', 'delay', [('var', 'L'), ('num', 1.0)]))])), ('bin', '>', ('call', 'abs', [('bin', '-', ('var', 'L'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('call', 'abs', [('bin', '-', ('var', 'H'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]))), ('bin', '+', ('bin', '+', ('call', 'abs', [('bin', '-', ('var', 'L'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('bin', '/', ('call', 'abs', [('bin', '-', ('var', 'H'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('num', 2.0))), ('bin', '/', ('call', 'abs', [('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 1.0)]), ('call', 'delay', [('var', 'O'), ('num', 1.0)]))]), ('num', 4.0))), ('bin', '+', ('call', 'abs', [('bin', '-', ('var', 'H'), ('call', 'delay', [('var', 'L'), ('num', 1.0)]))]), ('bin', '/', ('call', 'abs', [('bin', '-', ('call', 'delay', [('var', 'C'), ('num', 1.0)]), ('call', 'delay', [('var', 'O'), ('num', 1.0)]))]), ('num', 4.0)))))), ('call', 'max', [('call', 'abs', [('bin', '-', ('var', 'H'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))]), ('call', 'abs', [('bin', '-', ('var', 'L'), ('call', 'delay', [('var', 'C'), ('num', 1.0)]))])]))}

@register_factor
@fixed_factor('alpha191_137_2d', {})
class Factor_alpha191_137_2d(PublicFactor):
    name = 'alpha191_137_2d'
    description = '16*(C-DELAY(C,1)+(C-O)/2+DELAY(C,1)-DELAY(O,1))/((ABS(H-DELAY(C,1))>ABS(L-DELAY(C,1))&ABS(H-DELAY(C,1))>ABS(H-DELAY(L,1))?ABS(H-DELAY(C,1))+ABS(L-DELAY(C,1))/2+ABS(DELAY(C,1)-DELAY(O,1))/4:(ABS(L-DELAY(C,1))>ABS(H-DELAY(L,1))&ABS(L-DELAY(C,1))>ABS(H-DELAY(C,1))?ABS(L-DELAY(C,1))+ABS(H-DELAY(C,1))/2+ABS(DELAY(C,1)-DELAY(O,1))/4:ABS(H-DELAY(L,1))+ABS(DELAY(C,1)-DELAY(O,1))/4)))*MAX(ABS(H-DELAY(C,1)),ABS(L-DELAY(C,1)))；原目录：GTJA_Alpha191_137；追踪：PF00231；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
