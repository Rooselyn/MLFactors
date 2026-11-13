"""Pandas TA Classic

公式：源码算子/递推链：tpi = 2.0 * pi；cos_arr = cos(tpi * j_arr / period)；sin_arr = sin(tpi * j_arr / period)；输出=(sine, lead)；window = arr[i - period + 1:i + 1][::-1]；phase += pi / 2.0；lead[i] = sin(phase + pi / 4.0)；phase = arctan(ip / rp)；phase = tpi / 2.0 * (-1.0 if ip < 0 else 1.0)；phase += pi；phase += tpi；phase -= tpi；源码算子/递推链：输出=df；输出=None；_pad = len(close) - _size；sine_arr = concatenate([[nan] * _pad, result[0]])；lead_arr = concatenate([[nan] * _pad, result[1]])；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/cycles/msw.py#L14)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'period': 5, 'offset': 0}；只输出'MSW_SINE_5'；原目录：msw（period=None）；追踪：PF01177；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_msw_msw_sine_5_5d', 'root_function': 'f_1eba4b78be_msw', 'required_inputs': ['close'], 'parameters': {'period': 5, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'MSW_SINE_5', 'gate_bars': 1, 'kernel': 'kernel_ab77e3a05a4de296', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_msw_msw_sine_5_5d', {})
class Factor_ptac_msw_msw_sine_5_5d(PublicFactor):
    name = 'ptac_msw_msw_sine_5_5d'
    description = "源码算子/递推链：tpi = 2.0 * pi；cos_arr = cos(tpi * j_arr / period)；sin_arr = sin(tpi * j_arr / period)；输出=(sine, lead)；window = arr[i - period + 1:i + 1][::-1]；phase += pi / 2.0；lead[i] = sin(phase + pi / 4.0)；phase = arctan(ip / rp)；phase = tpi / 2.0 * (-1.0 if ip < 0 else 1.0)；phase += pi；phase += tpi；phase -= tpi；源码算子/递推链：输出=df；输出=None；_pad = len(close) - _size；sine_arr = concatenate([[nan] * _pad, result[0]])；lead_arr = concatenate([[nan] * _pad, result[1]])；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/cycles/msw.py#L14)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'period': 5, 'offset': 0}；只输出'MSW_SINE_5'；原目录：msw（period=None）；追踪：PF01177；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
