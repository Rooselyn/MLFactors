"""国泰君安 Alpha191

公式：((((DELTA((SUM(C,100)/100),100)/DELAY(C,100))<0.05)||((DELTA((SUM(C,100)/100),100)/DELAY(C,100))==0.05))?(-1*(C-TSMIN(C,100))):(-1*DELTA(C,3)))；原目录：GTJA_Alpha191_098；追踪：PF00195；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_098_200d', 'engine': 'alpha', 'kind': 191, 'tree': ('if', ('bin', '||', ('bin', '<', ('bin', '/', ('call', 'delta', [('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 100.0)]), ('num', 100.0)), ('num', 100.0)]), ('call', 'delay', [('var', 'C'), ('num', 100.0)])), ('num', 0.05)), ('bin', '==', ('bin', '/', ('call', 'delta', [('bin', '/', ('call', 'sum', [('var', 'C'), ('num', 100.0)]), ('num', 100.0)), ('num', 100.0)]), ('call', 'delay', [('var', 'C'), ('num', 100.0)])), ('num', 0.05))), ('bin', '*', ('unary', '-', ('num', 1.0)), ('bin', '-', ('var', 'C'), ('call', 'tsmin', [('var', 'C'), ('num', 100.0)]))), ('bin', '*', ('unary', '-', ('num', 1.0)), ('call', 'delta', [('var', 'C'), ('num', 3.0)])))}

@register_factor
@fixed_factor('alpha191_098_200d', {})
class Factor_alpha191_098_200d(PublicFactor):
    name = 'alpha191_098_200d'
    description = '((((DELTA((SUM(C,100)/100),100)/DELAY(C,100))<0.05)||((DELTA((SUM(C,100)/100),100)/DELAY(C,100))==0.05))?(-1*(C-TSMIN(C,100))):(-1*DELTA(C,3)))；原目录：GTJA_Alpha191_098；追踪：PF00195；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
