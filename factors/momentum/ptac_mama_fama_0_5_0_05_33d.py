"""Pandas TA Classic

公式：源码算子/递推链：rad2deg = 180.0 / pi；period_wma_sub = close_arr[0] + close_arr[1] + close_arr[2]；period_wma_sum = close_arr[0] * 1.0 + close_arr[1] * 2.0 + close_arr[2] * 3.0；输出=(mama_out, fama_out)；period_wma_sub += new_price；period_wma_sub -= trailing_wma_value；period_wma_sum += new_price * 4.0；trailing_wma_idx += 1；smoothed_value = period_wma_sum * 0.1；period_wma_sum -= period_wma_sub；adjusted_prev_period = 0.075 * period + 0.54；period_wma_sub += today_value；period_wma_sum += today_value * 4.0；delta_phase = prev_phase - phase；mama_val = alpha * today_value + (1.0 - alpha) * mama_val；fama_val = 0.5 * alpha * mama_val + (1.0 - 0.5 * alpha) * fama_val；re = 0.2 * (I2 * prev_i2 + Q2 * prev_q2) + 0.8 * re；im = 0.2 * (I2 * prev_q2 - Q2 * prev_i2) + 0.8 * im；period = min(period, 1.5 * prev_period)；period = max(period, 0.67 * prev_period)；period = 0.2 * period + 0.8 * prev_period；today += 1；ht = a * smoothed_value；detrender = -det_even[hilbert_idx]；源码算子/递推链：输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/mama.py#L248)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fastlimit': 0.5, 'slowlimit': 0.05, 'talib': False, 'offset': 0}；只输出'FAMA_0.5_0.05'；原目录：mama（fastlimit=None, slowlimit=None）；追踪：PF01233；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_mama_fama_0_5_0_05_33d', 'root_function': 'f_db6b093f09_mama', 'required_inputs': ['close'], 'parameters': {'fastlimit': 0.5, 'slowlimit': 0.05, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'FAMA_0.5_0.05', 'gate_bars': 1, 'kernel': 'kernel_37bbdb153fc87189', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_mama_fama_0_5_0_05_33d', {})
class Factor_ptac_mama_fama_0_5_0_05_33d(PublicFactor):
    name = 'ptac_mama_fama_0_5_0_05_33d'
    description = "源码算子/递推链：rad2deg = 180.0 / pi；period_wma_sub = close_arr[0] + close_arr[1] + close_arr[2]；period_wma_sum = close_arr[0] * 1.0 + close_arr[1] * 2.0 + close_arr[2] * 3.0；输出=(mama_out, fama_out)；period_wma_sub += new_price；period_wma_sub -= trailing_wma_value；period_wma_sum += new_price * 4.0；trailing_wma_idx += 1；smoothed_value = period_wma_sum * 0.1；period_wma_sum -= period_wma_sub；adjusted_prev_period = 0.075 * period + 0.54；period_wma_sub += today_value；period_wma_sum += today_value * 4.0；delta_phase = prev_phase - phase；mama_val = alpha * today_value + (1.0 - alpha) * mama_val；fama_val = 0.5 * alpha * mama_val + (1.0 - 0.5 * alpha) * fama_val；re = 0.2 * (I2 * prev_i2 + Q2 * prev_q2) + 0.8 * re；im = 0.2 * (I2 * prev_q2 - Q2 * prev_i2) + 0.8 * im；period = min(period, 1.5 * prev_period)；period = max(period, 0.67 * prev_period)；period = 0.2 * period + 0.8 * prev_period；today += 1；ht = a * smoothed_value；detrender = -det_even[hilbert_idx]；源码算子/递推链：输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/mama.py#L248)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fastlimit': 0.5, 'slowlimit': 0.05, 'talib': False, 'offset': 0}；只输出'FAMA_0.5_0.05'；原目录：mama（fastlimit=None, slowlimit=None）；追踪：PF01233；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
