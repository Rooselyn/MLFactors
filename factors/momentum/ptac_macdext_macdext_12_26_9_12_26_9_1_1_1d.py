"""Pandas TA Classic

公式：DIF=MA_type_fast(C,fast)−MA_type_slow(C,slow)；Signal=MA_type_signal(DIF,signal)；Hist=DIF−Signal；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/macdext.py#L25)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'signal': 9, 'fastmatype': 1, 'slowmatype': 1, 'signalmatype': 1, 'talib': False, 'offset': 0}；只输出'MACDEXT_12_26_9'；原目录：macdext（fast=12, slow=26, signal=9）；追踪：PF01195；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_macdext_macdext_12_26_9_12_26_9_1_1_1d', 'root_function': 'f_a8a48d4d79_macdext', 'required_inputs': ['close'], 'parameters': {'fast': 12, 'slow': 26, 'signal': 9, 'fastmatype': 1, 'slowmatype': 1, 'signalmatype': 1, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'MACDEXT_12_26_9', 'gate_bars': 1, 'kernel': 'kernel_8e12bcef06fd9ff6', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_macdext_macdext_12_26_9_12_26_9_1_1_1d', {})
class Factor_ptac_macdext_macdext_12_26_9_12_26_9_1_1_1d(PublicFactor):
    name = 'ptac_macdext_macdext_12_26_9_12_26_9_1_1_1d'
    description = "DIF=MA_type_fast(C,fast)−MA_type_slow(C,slow)；Signal=MA_type_signal(DIF,signal)；Hist=DIF−Signal；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/macdext.py#L25)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'signal': 9, 'fastmatype': 1, 'slowmatype': 1, 'signalmatype': 1, 'talib': False, 'offset': 0}；只输出'MACDEXT_12_26_9'；原目录：macdext（fast=12, slow=26, signal=9）；追踪：PF01195；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
