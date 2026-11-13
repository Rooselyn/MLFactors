"""Pandas TA Classic

公式：源码算子/递推链：输出=entropy；输出=None；result_arr[length - 1:] = entropy_vals；p = where(valid[:, None], windows / window_sums[:, None], nan)；p_term = -p * log(p) / log(base)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/entropy.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'base': 2.0, 'offset': 0}；只输出'ENTP_10'；原目录：entropy（length=10）；追踪：PF01257；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_entropy_entp_10_10d', 'root_function': 'f_c98810ae49_entropy', 'required_inputs': ['close'], 'parameters': {'length': 10, 'base': 2.0, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'ENTP_10', 'gate_bars': 1, 'kernel': 'kernel_3305e9aec0fe4374', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_entropy_entp_10_10d', {})
class Factor_ptac_entropy_entp_10_10d(PublicFactor):
    name = 'ptac_entropy_entp_10_10d'
    description = "源码算子/递推链：输出=entropy；输出=None；result_arr[length - 1:] = entropy_vals；p = where(valid[:, None], windows / window_sums[:, None], nan)；p_term = -p * log(p) / log(base)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/entropy.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'base': 2.0, 'offset': 0}；只输出'ENTP_10'；原目录：entropy（length=10）；追踪：PF01257；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
