"""Pandas TA Classic

公式：源码算子/递推链：输出=zscore；输出=None；window_mean = windows.mean(axis=1)；window_std = windows.std(axis=1, ddof=ddof)；denominator = std * window_std；result_arr[length - 1:] = where(degenerate_zero(denominator), 0.0, scores)；scores = (values[length - 1:] - window_mean) / denominator；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/zscore.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'std': 1, 'offset': 0, 'ddof': 1}；只输出'ZS_30'；原目录：zscore（length=30, ddof=1）；追踪：PF01267；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_zscore_zs_30_30d', 'root_function': 'f_b8c6dc9ea5_zscore', 'required_inputs': ['close'], 'parameters': {'length': 30, 'std': 1, 'offset': 0, 'ddof': 1}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'ZS_30', 'gate_bars': 1, 'kernel': 'kernel_e690c20ec09d9ade', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_zscore_zs_30_30d', {})
class Factor_ptac_zscore_zs_30_30d(PublicFactor):
    name = 'ptac_zscore_zs_30_30d'
    description = "源码算子/递推链：输出=zscore；输出=None；window_mean = windows.mean(axis=1)；window_std = windows.std(axis=1, ddof=ddof)；denominator = std * window_std；result_arr[length - 1:] = where(degenerate_zero(denominator), 0.0, scores)；scores = (values[length - 1:] - window_mean) / denominator；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/statistics/zscore.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'std': 1, 'offset': 0, 'ddof': 1}；只输出'ZS_30'；原目录：zscore（length=30, ddof=1）；追踪：PF01267；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
