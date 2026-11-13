"""国泰君安 Alpha191

公式：MEAN(ABS(SUM((LD>0&LD>HD)?LD:0,14)*100/SUM(TR,14)-SUM((HD>0&HD>LD)?HD:0,14)*100/SUM(TR,14))/(SUM((LD>0&LD>HD)?LD:0,14)*100/SUM(TR,14)+SUM((HD>0&HD>LD)?HD:0,14)*100/SUM(TR,14))*100,6)；原目录：GTJA_Alpha191_172；追踪：PF00266；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_172_20d', 'engine': 'alpha', 'kind': 191, 'tree': ['call', 'mean', [['bin', '*', ['bin', '/', ['call', 'abs', [['bin', '-', ['bin', '/', ['bin', '*', ['call', 'sum', [['if', ['bin', '&&', ['bin', '>', ['var', 'LD'], ['num', 0.0]], ['bin', '>', ['var', 'LD'], ['var', 'HD']]], ['var', 'LD'], ['num', 0.0]], ['num', 14.0]]], ['num', 100.0]], ['call', 'sum', [['var', 'TR'], ['num', 14.0]]]], ['bin', '/', ['bin', '*', ['call', 'sum', [['if', ['bin', '&&', ['bin', '>', ['var', 'HD'], ['num', 0.0]], ['bin', '>', ['var', 'HD'], ['var', 'LD']]], ['var', 'HD'], ['num', 0.0]], ['num', 14.0]]], ['num', 100.0]], ['call', 'sum', [['var', 'TR'], ['num', 14.0]]]]]]], ['bin', '+', ['bin', '/', ['bin', '*', ['call', 'sum', [['if', ['bin', '&&', ['bin', '>', ['var', 'LD'], ['num', 0.0]], ['bin', '>', ['var', 'LD'], ['var', 'HD']]], ['var', 'LD'], ['num', 0.0]], ['num', 14.0]]], ['num', 100.0]], ['call', 'sum', [['var', 'TR'], ['num', 14.0]]]], ['bin', '/', ['bin', '*', ['call', 'sum', [['if', ['bin', '&&', ['bin', '>', ['var', 'HD'], ['num', 0.0]], ['bin', '>', ['var', 'HD'], ['var', 'LD']]], ['var', 'HD'], ['num', 0.0]], ['num', 14.0]]], ['num', 100.0]], ['call', 'sum', [['var', 'TR'], ['num', 14.0]]]]]], ['num', 100.0]], ['num', 6.0]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_172_20d', {})
class Factor_alpha191_172_20d(PublicFactor):
    name = 'alpha191_172_20d'
    description = 'MEAN(ABS(SUM((LD>0&LD>HD)?LD:0,14)*100/SUM(TR,14)-SUM((HD>0&HD>LD)?HD:0,14)*100/SUM(TR,14))/(SUM((LD>0&LD>HD)?LD:0,14)*100/SUM(TR,14)+SUM((HD>0&HD>LD)?HD:0,14)*100/SUM(TR,14))*100,6)；原目录：GTJA_Alpha191_172；追踪：PF00266；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
