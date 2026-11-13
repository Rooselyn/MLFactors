"""国泰君安 Alpha191

公式：REGBETA_FILTERED(C,BC,252)；FILTER明确定义为最近252个中证500下跌且股指/个股日收益均有效的观测；非252个连续交易日。以这些配对样本计算含截距OLS斜率，未新增样本的日期沿用同一已知样本集重算；不足252对为NaN。；原目录：GTJA_Alpha191_149；追踪：PF00243；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'benchmark_close': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'close', symbol_column=None, expression='close', filters=(("ts_code", "000905.SH"),)),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'alpha191_149_local_alld', 'engine': 'alpha', 'kind': 191, 'tree': ['call', 'regbeta_filtered', [['var', 'C'], ['var', 'BC'], ['num', 252.0]]], 'kernel': 'kernel_380a524944b9ff75', 'root_function': 'alpha191_eval'}

@register_factor
@fixed_factor('alpha191_149_local_alld', {})
class Factor_alpha191_149_local_alld(PublicFactor):
    name = 'alpha191_149_local_alld'
    description = 'REGBETA_FILTERED(C,BC,252)；FILTER明确定义为最近252个中证500下跌且股指/个股日收益均有效的观测；非252个连续交易日。以这些配对样本计算含截距OLS斜率，未新增样本的日期沿用同一已知样本集重算；不足252对为NaN。；原目录：GTJA_Alpha191_149；追踪：PF00243；[来源](https://github.com/ABO3/References/blob/master/20170615-国泰君安-数量化专题之九十三：基于短周期价量特征的多因子选股体系.pdf)。'
    INPUTS = INPUTS
    SPEC = SPEC
