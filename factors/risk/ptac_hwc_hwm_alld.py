"""Pandas TA Classic

公式：源码算子/递推链：输出=(result_arr, upper_arr, lower_arr)；F = (1.0 - na) * (last_f + last_v + 0.5 * last_a) + na * c_arr[i]；V = (1.0 - nb) * (last_v + last_a) + nb * (F - last_f)；A = (1.0 - nc) * last_a + nc * (V - last_v)；result_arr[i] = F + V + 0.5 * A；var = (1.0 - nd) * last_var + nd * (last_price - last_result) * (last_price - last_result)；stddev = last_var ^ 0.5；upper_arr[i] = result_arr[i] + scalar * stddev；lower_arr[i] = result_arr[i] - scalar * stddev；源码算子/递推链：输出=df；源码算子/递推链：输出=_hwc_build_df(hwc_s, hwc_upper, hwc_lower, hwc_width, hwc_pctwidth, channel_eval)；输出=None；hwc_width = Series(upper_arr - lower_arr, index=close.index)；denom = upper_arr - lower_arr；numer = c_arr - lower_arr；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/hwc.py#L75)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'na': 0.2, 'nb': 0.1, 'nc': 0.1, 'nd': 0.1, 'scalar': 1, 'channel_eval': False, 'offset': 0}；只输出'HWM'；原目录：hwc（na=None, nb=None, nc=None, nd=None, scalar=None, channel_eval=None）；追踪：PF01302；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_hwc_hwm_alld', 'root_function': 'f_9c0db4852d_hwc', 'required_inputs': ['close'], 'parameters': {'na': 0.2, 'nb': 0.1, 'nc': 0.1, 'nd': 0.1, 'scalar': 1, 'channel_eval': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'HWM', 'gate_bars': 1, 'kernel': 'kernel_a72070bf5b37a858', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_hwc_hwm_alld', {})
class Factor_ptac_hwc_hwm_alld(PublicFactor):
    name = 'ptac_hwc_hwm_alld'
    description = "源码算子/递推链：输出=(result_arr, upper_arr, lower_arr)；F = (1.0 - na) * (last_f + last_v + 0.5 * last_a) + na * c_arr[i]；V = (1.0 - nb) * (last_v + last_a) + nb * (F - last_f)；A = (1.0 - nc) * last_a + nc * (V - last_v)；result_arr[i] = F + V + 0.5 * A；var = (1.0 - nd) * last_var + nd * (last_price - last_result) * (last_price - last_result)；stddev = last_var ^ 0.5；upper_arr[i] = result_arr[i] + scalar * stddev；lower_arr[i] = result_arr[i] - scalar * stddev；源码算子/递推链：输出=df；源码算子/递推链：输出=_hwc_build_df(hwc_s, hwc_upper, hwc_lower, hwc_width, hwc_pctwidth, channel_eval)；输出=None；hwc_width = Series(upper_arr - lower_arr, index=close.index)；denom = upper_arr - lower_arr；numer = c_arr - lower_arr；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/hwc.py#L75)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'na': 0.2, 'nb': 0.1, 'nc': 0.1, 'nd': 0.1, 'scalar': 1, 'channel_eval': False, 'offset': 0}；只输出'HWM'；原目录：hwc（na=None, nb=None, nc=None, nd=None, scalar=None, channel_eval=None）；追踪：PF01302；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
