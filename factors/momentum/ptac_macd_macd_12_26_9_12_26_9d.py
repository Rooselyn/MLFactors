"""Pandas TA Classic

公式：DIF=EMA(C,fast)−EMA(C,slow)；Signal=EMA(DIF,signal)；Hist=DIF−Signal；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/macd.py#L49)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'signal': 9, 'talib': False, 'offset': 0}；只输出'MACD_12_26_9'；原目录：macd（fast=12, slow=26, signal=9）；追踪：PF01194；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_macd_macd_12_26_9_12_26_9d', 'root_function': 'f_fe07d2dbbf_macd', 'required_inputs': ['close'], 'parameters': {'fast': 12, 'slow': 26, 'signal': 9, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'MACD_12_26_9', 'gate_bars': 1, 'kernel': 'kernel_30e3ae4e2516353c', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_macd_macd_12_26_9_12_26_9d', {})
class Factor_ptac_macd_macd_12_26_9_12_26_9d(PublicFactor):
    name = 'ptac_macd_macd_12_26_9_12_26_9d'
    description = "DIF=EMA(C,fast)−EMA(C,slow)；Signal=EMA(DIF,signal)；Hist=DIF−Signal；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/macd.py#L49)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'signal': 9, 'talib': False, 'offset': 0}；只输出'MACD_12_26_9'；原目录：macd（fast=12, slow=26, signal=9）；追踪：PF01194；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
