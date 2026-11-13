"""Pandas TA Classic

公式：源码算子/递推链：输出=skew；输出=None；result = n_eff * sqrt(n_eff - 1) / (n_eff - 2) * m3 / m2 ^ 1.5；n_eff[pos] = pos + 1；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/skew.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'offset': 0}；只输出'SKEW_30'；原目录：skew（length=30）；追踪：PF01262；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_skew_skew_30_30d', 'root_function': 'f_a677161d14_skew', 'required_inputs': ['close'], 'parameters': {'length': 30, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'SKEW_30', 'gate_bars': 1, 'kernel': 'kernel_7e38b21f36136045', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_skew_skew_30_30d', {})
class Factor_ptac_skew_skew_30_30d(PublicFactor):
    name = 'ptac_skew_skew_30_30d'
    description = "源码算子/递推链：输出=skew；输出=None；result = n_eff * sqrt(n_eff - 1) / (n_eff - 2) * m3 / m2 ^ 1.5；n_eff[pos] = pos + 1；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/skew.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'offset': 0}；只输出'SKEW_30'；原目录：skew（length=30）；追踪：PF01262；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
