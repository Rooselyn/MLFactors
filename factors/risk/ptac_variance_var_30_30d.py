"""Pandas TA Classic

公式：源码算子/递推链：输出=result_arr；result_arr[length - 1:] = windows.var(axis=1, ddof=ddof)；w = values[:pos + 1]；源码算子/递推链：输出=variance；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/variance.py#L45)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'ddof': 0, 'talib': False, 'offset': 0}；只输出'VAR_30'；原目录：variance（length=30, ddof=0）；追踪：PF01266；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_variance_var_30_30d', 'root_function': 'f_6fe614a5c9_variance', 'required_inputs': ['close'], 'parameters': {'length': 30, 'ddof': 0, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'VAR_30', 'gate_bars': 1, 'kernel': 'kernel_7503b03deeb53c11', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_variance_var_30_30d', {})
class Factor_ptac_variance_var_30_30d(PublicFactor):
    name = 'ptac_variance_var_30_30d'
    description = "源码算子/递推链：输出=result_arr；result_arr[length - 1:] = windows.var(axis=1, ddof=ddof)；w = values[:pos + 1]；源码算子/递推链：输出=variance；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/variance.py#L45)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'ddof': 0, 'talib': False, 'offset': 0}；只输出'VAR_30'；原目录：variance（length=30, ddof=0）；追踪：PF01266；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
