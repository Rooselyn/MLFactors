"""Pandas TA Classic

公式：源码算子/递推链：up = high - high.shift(drift)；dn = low.shift(drift) - low；_dmn = (((dn > up) & (dn > 0)) * dn).apply(zero).iloc[-1]；输出=_dmn > 0；源码算子/递推链：输出=(long_arr, short_arr, af_arr, reversal_arr)；_sar = sar + af * (ep - sar)；_sar = max(h_arr[row - 1], h_arr[max(0, row - 2)], _sar)；_sar = min(l_arr[row - 1], l_arr[max(0, row - 2)], _sar)；af = min(af + af0, max_af)；源码算子/递推链：输出=psardf；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/psar.py#L73)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'af0': 0.02, 'af': 0.02, 'max_af': 0.2, 'talib': False, 'offset': 0}；只输出'PSARs_0.02_0.2'；原目录：psar（close=None, af0=None, af=None, max_af=None）；追踪：PF01285；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_psar_psars_0_02_0_2_alld', 'root_function': 'f_9223b9771a_psar', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'af0': 0.02, 'af': 0.02, 'max_af': 0.2, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'PSARs_0.02_0.2', 'gate_bars': 1, 'kernel': 'kernel_081d6cb10c61cca8', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_psar_psars_0_02_0_2_alld', {})
class Factor_ptac_psar_psars_0_02_0_2_alld(PublicFactor):
    name = 'ptac_psar_psars_0_02_0_2_alld'
    description = "源码算子/递推链：up = high - high.shift(drift)；dn = low.shift(drift) - low；_dmn = (((dn > up) & (dn > 0)) * dn).apply(zero).iloc[-1]；输出=_dmn > 0；源码算子/递推链：输出=(long_arr, short_arr, af_arr, reversal_arr)；_sar = sar + af * (ep - sar)；_sar = max(h_arr[row - 1], h_arr[max(0, row - 2)], _sar)；_sar = min(l_arr[row - 1], l_arr[max(0, row - 2)], _sar)；af = min(af + af0, max_af)；源码算子/递推链：输出=psardf；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/psar.py#L73)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'af0': 0.02, 'af': 0.02, 'max_af': 0.2, 'talib': False, 'offset': 0}；只输出'PSARs_0.02_0.2'；原目录：psar（close=None, af0=None, af=None, max_af=None）；追踪：PF01285；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
