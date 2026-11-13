"""国泰君安 Alpha191

公式：RANK(DELTA(((((H+L)/2)*0.2)+(P*0.8)),4)*-1)；原目录：GTJA_Alpha191_008；追踪：PF00109；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_008_5d', 'engine': 'alpha', 'kind': 191, 'tree': ('call', 'rank', [('bin', '*', ('call', 'delta', [('bin', '+', ('bin', '*', ('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)), ('num', 0.2)), ('bin', '*', ('var', 'P'), ('num', 0.8))), ('num', 4.0)]), ('unary', '-', ('num', 1.0)))])}

@register_factor
@fixed_factor('alpha191_008_5d', {})
class Factor_alpha191_008_5d(PublicFactor):
    name = 'alpha191_008_5d'
    description = 'RANK(DELTA(((((H+L)/2)*0.2)+(P*0.8)),4)*-1)；原目录：GTJA_Alpha191_008；追踪：PF00109；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
