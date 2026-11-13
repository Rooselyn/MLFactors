"""Pandas TA Classic

公式：源码算子/递推链：factor = exp(-1.0 / length)；输出=result；输出=None；result[i] = arr[i] if arr[i] >= result[i - 1] * factor else max(arr[i], result[i - 1] * factor)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/edecay.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 5, 'offset': 0}；只输出'EDECAY_5'；原目录：edecay（length=5）；追踪：PF01279；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_edecay_edecay_5_5d', 'root_function': 'f_237a38d81b_edecay', 'required_inputs': ['close'], 'parameters': {'length': 5, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'EDECAY_5', 'gate_bars': 1, 'kernel': 'kernel_ce67080133193f8c', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_edecay_edecay_5_5d', {})
class Factor_ptac_edecay_edecay_5_5d(PublicFactor):
    name = 'ptac_edecay_edecay_5_5d'
    description = "源码算子/递推链：factor = exp(-1.0 / length)；输出=result；输出=None；result[i] = arr[i] if arr[i] >= result[i - 1] * factor else max(arr[i], result[i - 1] * factor)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/edecay.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 5, 'offset': 0}；只输出'EDECAY_5'；原目录：edecay（length=5）；追踪：PF01279；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
