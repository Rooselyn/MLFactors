"""国泰君安 Alpha191

公式：((RANK((P-MIN(P,12)))^TSRANK(CORR(TSRANK(P,20),TSRANK(MEAN(V,60),2),18),3))*-1)；原目录：GTJA_Alpha191_121；追踪：PF00215；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'alpha191_121_80d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '*', ['bin', '^', ['call', 'rank', [['bin', '-', ['var', 'P'], ['call', 'min', [['var', 'P'], ['num', 12.0]]]]]], ['call', 'tsrank', [['call', 'corr', [['call', 'tsrank', [['var', 'P'], ['num', 20.0]]], ['call', 'tsrank', [['call', 'mean', [['var', 'V'], ['num', 60.0]]], ['num', 2.0]]], ['num', 18.0]]], ['num', 3.0]]]], ['unary', '-', ['num', 1.0]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_121_80d', {})
class Factor_alpha191_121_80d(PublicFactor):
    name = 'alpha191_121_80d'
    description = '((RANK((P-MIN(P,12)))^TSRANK(CORR(TSRANK(P,20),TSRANK(MEAN(V,60),2),18),3))*-1)；原目录：GTJA_Alpha191_121；追踪：PF00215；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
