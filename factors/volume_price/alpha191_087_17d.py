"""国泰君安 Alpha191

公式：((RANK(DECAYLINEAR(DELTA(P,4),7))+TSRANK(DECAYLINEAR(((((L*0.9)+(L*0.1))-P)/(O-((H+L)/2))),11),7))*-1)；原目录：GTJA_Alpha191_087；追踪：PF00184；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'alpha191_087_17d', 'engine': 'alpha', 'kind': 191, 'tree': ('bin', '*', ('bin', '+', ('call', 'rank', [('call', 'decaylinear', [('call', 'delta', [('var', 'P'), ('num', 4.0)]), ('num', 7.0)])]), ('call', 'tsrank', [('call', 'decaylinear', [('bin', '/', ('bin', '-', ('bin', '+', ('bin', '*', ('var', 'L'), ('num', 0.9)), ('bin', '*', ('var', 'L'), ('num', 0.1))), ('var', 'P')), ('bin', '-', ('var', 'O'), ('bin', '/', ('bin', '+', ('var', 'H'), ('var', 'L')), ('num', 2.0)))), ('num', 11.0)]), ('num', 7.0)])), ('unary', '-', ('num', 1.0)))}

@register_factor
@fixed_factor('alpha191_087_17d', {})
class Factor_alpha191_087_17d(PublicFactor):
    name = 'alpha191_087_17d'
    description = '((RANK(DECAYLINEAR(DELTA(P,4),7))+TSRANK(DECAYLINEAR(((((L*0.9)+(L*0.1))-P)/(O-((H+L)/2))),11),7))*-1)；原目录：GTJA_Alpha191_087；追踪：PF00184；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
