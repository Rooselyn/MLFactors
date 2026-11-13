"""国泰君安 Alpha191

公式：COUNT(C>O&BC<BO,50)/COUNT(BC<BO,50)；原目录：GTJA_Alpha191_075；追踪：PF00173；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'benchmark_close': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'close', symbol_column=None, expression='close', filters=(("ts_code", "000905.SH"),)),
    'benchmark_open': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'open', symbol_column=None, expression='open', filters=(("ts_code", "000905.SH"),)),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'alpha191_075_50d', 'engine': 'alpha', 'kind': 191, 'tree': ['bin', '/', ['call', 'count', [['bin', '&&', ['bin', '>', ['var', 'C'], ['var', 'O']], ['bin', '<', ['var', 'BC'], ['var', 'BO']]], ['num', 50.0]]], ['call', 'count', [['bin', '<', ['var', 'BC'], ['var', 'BO']], ['num', 50.0]]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_075_50d', {})
class Factor_alpha191_075_50d(PublicFactor):
    name = 'alpha191_075_50d'
    description = 'COUNT(C>O&BC<BO,50)/COUNT(BC<BO,50)；原目录：GTJA_Alpha191_075；追踪：PF00173；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
