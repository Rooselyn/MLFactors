"""国泰君安 Alpha191

公式：(SUM(DTM,20)>SUM(DBM,20)?(SUM(DTM,20)-SUM(DBM,20))/SUM(DTM,20):(SUM(DTM,20)=SUM(DBM,20)?0:(SUM(DTM,20)-SUM(DBM,20))/SUM(DBM,20)))；原目录：GTJA_Alpha191_069；追踪：PF00167；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
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
SPEC = {'name': 'alpha191_069_local_21d', 'engine': 'alpha', 'kind': 191, 'tree': ['if', ['bin', '>', ['call', 'sum', [['var', 'DTM'], ['num', 20.0]]], ['call', 'sum', [['var', 'DBM'], ['num', 20.0]]]], ['bin', '/', ['bin', '-', ['call', 'sum', [['var', 'DTM'], ['num', 20.0]]], ['call', 'sum', [['var', 'DBM'], ['num', 20.0]]]], ['call', 'sum', [['var', 'DTM'], ['num', 20.0]]]], ['if', ['bin', '==', ['call', 'sum', [['var', 'DTM'], ['num', 20.0]]], ['call', 'sum', [['var', 'DBM'], ['num', 20.0]]]], ['num', 0.0], ['bin', '/', ['bin', '-', ['call', 'sum', [['var', 'DTM'], ['num', 20.0]]], ['call', 'sum', [['var', 'DBM'], ['num', 20.0]]]], ['call', 'sum', [['var', 'DBM'], ['num', 20.0]]]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_069_local_21d', {})
class Factor_alpha191_069_local_21d(PublicFactor):
    name = 'alpha191_069_local_21d'
    description = '(SUM(DTM,20)>SUM(DBM,20)?(SUM(DTM,20)-SUM(DBM,20))/SUM(DTM,20):(SUM(DTM,20)=SUM(DBM,20)?0:(SUM(DTM,20)-SUM(DBM,20))/SUM(DBM,20)))；原目录：GTJA_Alpha191_069；追踪：PF00167；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
