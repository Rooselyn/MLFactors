"""Pandas TA Classic

公式：DIF=EMA(C,12)−EMA(C,26)；Signal=EMA(DIF,signal)；Hist=DIF−Signal；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/macdfix.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'signal': 9, 'talib': False, 'offset': 0}；只输出'MACDFIXh_9_9'；原目录：macdfix（signal=9）；追踪：PF01196；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_macdfix_macdfixh_9_9_9d', 'root_function': 'f_01d000a91f_macdfix', 'required_inputs': ['close'], 'parameters': {'signal': 9, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'MACDFIXh_9_9', 'gate_bars': 1, 'kernel': 'kernel_d36edd9e23e21efa', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_macdfix_macdfixh_9_9_9d', {})
class Factor_ptac_macdfix_macdfixh_9_9_9d(PublicFactor):
    name = 'ptac_macdfix_macdfixh_9_9_9d'
    description = "DIF=EMA(C,12)−EMA(C,26)；Signal=EMA(DIF,signal)；Hist=DIF−Signal；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/macdfix.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'signal': 9, 'talib': False, 'offset': 0}；只输出'MACDFIXh_9_9'；原目录：macdfix（signal=9）；追踪：PF01196；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
