"""国泰君安 Alpha191

公式：SUM(((C/DELAY(C,1)-1)-MEAN((C/DELAY(C,1)-1),20))-(BC-MEAN(BC,20))^2,20)/SUM((BC-MEAN(BC,20))^3,20)；原目录：GTJA_Alpha191_181；追踪：PF00275；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'benchmark_close': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'close', symbol_column=None, expression='close', filters=(("ts_code", "000905.SH"),)),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_181_local_40d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '/', ['call', 'sum', [['bin', '-', ['bin', '-', ['bin', '-', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 1.0]], ['call', 'mean', [['bin', '-', ['bin', '/', ['var', 'C'], ['call', 'delay', [['var', 'C'], ['num', 1.0]]]], ['num', 1.0]], ['num', 20.0]]]], ['bin', '^', ['bin', '-', ['var', 'BC'], ['call', 'mean', [['var', 'BC'], ['num', 20.0]]]], ['num', 2.0]]], ['num', 20.0]]], ['call', 'sum', [['bin', '^', ['bin', '-', ['var', 'BC'], ['call', 'mean', [['var', 'BC'], ['num', 20.0]]]], ['num', 3.0]], ['num', 20.0]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_181_local_40d', {})
class Factor_alpha191_181_local_40d(PublicFactor):
    name = 'alpha191_181_local_40d'
    description = 'SUM(((C/DELAY(C,1)-1)-MEAN((C/DELAY(C,1)-1),20))-(BC-MEAN(BC,20))^2,20)/SUM((BC-MEAN(BC,20))^3,20)；原目录：GTJA_Alpha191_181；追踪：PF00275；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
