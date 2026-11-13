"""Pandas TA Classic

公式：源码算子/递推链：输出=pmax_result；pmax_up_arr[i] = max(pmax_up_arr[i], pmax_up_arr[i - 1])；pmax_down_arr[i] = min(pmax_down_arr[i], pmax_down_arr[i - 1])；trend_arr[i] = -1；trend_arr[i] = trend_arr[i - 1]；源码算子/递推链：pmax_up = ma_value - multiplier * atr_value；pmax_down = ma_value + multiplier * atr_value；输出=pmax_s；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/pmax.py#L51)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'multiplier': 3.0, 'mamode': 'ema', 'offset': 0}；只输出'PMAX_E_10_3.0'；原目录：pmax（length=10, mamode='ema'）；追踪：PF01284；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_pmax_pmax_e_10_3_0_10d', 'root_function': 'f_da97339fc6_pmax', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'length': 10, 'multiplier': 3.0, 'mamode': 'ema', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'PMAX_E_10_3.0', 'gate_bars': 1, 'kernel': 'kernel_de1f2821ab422fb9', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_pmax_pmax_e_10_3_0_10d', {})
class Factor_ptac_pmax_pmax_e_10_3_0_10d(PublicFactor):
    name = 'ptac_pmax_pmax_e_10_3_0_10d'
    description = "源码算子/递推链：输出=pmax_result；pmax_up_arr[i] = max(pmax_up_arr[i], pmax_up_arr[i - 1])；pmax_down_arr[i] = min(pmax_down_arr[i], pmax_down_arr[i - 1])；trend_arr[i] = -1；trend_arr[i] = trend_arr[i - 1]；源码算子/递推链：pmax_up = ma_value - multiplier * atr_value；pmax_down = ma_value + multiplier * atr_value；输出=pmax_s；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/pmax.py#L51)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'multiplier': 3.0, 'mamode': 'ema', 'offset': 0}；只输出'PMAX_E_10_3.0'；原目录：pmax（length=10, mamode='ema'）；追踪：PF01284；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
