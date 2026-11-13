"""Pandas TA Classic

公式：源码算子/递推链：输出=(long_arr, short_arr, trend_arr, qqe_arr, qqe_long_arr, qqe_short_arr)；p_rsi = rsi_arr[i - 1]；c_long = long_arr[i - 1]；c_short = short_arr[i - 1]；p_long = long_arr[i - 2] if i >= 2 else 0.0；p_short = short_arr[i - 2] if i >= 2 else 0.0；trend_arr[i] = -1.0；trend_arr[i] = trend_arr[i - 1]；源码算子/递推链：wilders_length = 2 * length - 1；rsi_ma_tr = rsi_ma.diff(drift).abs()；dar = factor * _dar_ema；upperband = rsi_ma + dar；lowerband = rsi_ma - dar；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/qqe.py#L71)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'smooth': 5, 'factor': 4.236, 'mamode': 'ema', 'drift': 1, 'offset': 0}；只输出'QQEl_14_5_4.236'；原目录：qqe（length=14, smooth=5, factor=4.236, mamode='ema'）；追踪：PF01202；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_qqe_qqel_14_5_4_236_14d', 'root_function': 'f_2424864b7c_qqe', 'required_inputs': ['close'], 'parameters': {'length': 14, 'smooth': 5, 'factor': 4.236, 'mamode': 'ema', 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 2, 'output_label': 'QQEl_14_5_4.236', 'gate_bars': 1, 'kernel': 'kernel_1c12d7841c2317c2', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_qqe_qqel_14_5_4_236_14d', {})
class Factor_ptac_qqe_qqel_14_5_4_236_14d(PublicFactor):
    name = 'ptac_qqe_qqel_14_5_4_236_14d'
    description = "源码算子/递推链：输出=(long_arr, short_arr, trend_arr, qqe_arr, qqe_long_arr, qqe_short_arr)；p_rsi = rsi_arr[i - 1]；c_long = long_arr[i - 1]；c_short = short_arr[i - 1]；p_long = long_arr[i - 2] if i >= 2 else 0.0；p_short = short_arr[i - 2] if i >= 2 else 0.0；trend_arr[i] = -1.0；trend_arr[i] = trend_arr[i - 1]；源码算子/递推链：wilders_length = 2 * length - 1；rsi_ma_tr = rsi_ma.diff(drift).abs()；dar = factor * _dar_ema；upperband = rsi_ma + dar；lowerband = rsi_ma - dar；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/qqe.py#L71)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'smooth': 5, 'factor': 4.236, 'mamode': 'ema', 'drift': 1, 'offset': 0}；只输出'QQEl_14_5_4.236'；原目录：qqe（length=14, smooth=5, factor=4.236, mamode='ema'）；追踪：PF01202；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
