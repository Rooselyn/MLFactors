"""Pandas TA Classic

公式：MA(C,fast)−MA(C,slow)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/apo.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'mamode': 'sma', 'talib': False, 'offset': 0}；只输出'APO_12_26'；原目录：apo（fast=12, slow=26, mamode='sma'）；追踪：PF01178；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_apo_apo_12_26_12_26d', 'root_function': 'f_a4f5e9ab0b_apo', 'required_inputs': ['close'], 'parameters': {'fast': 12, 'slow': 26, 'mamode': 'sma', 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'APO_12_26', 'gate_bars': 1, 'kernel': 'kernel_4bcf8ba7572b6994', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_apo_apo_12_26_12_26d', {})
class Factor_ptac_apo_apo_12_26_12_26d(PublicFactor):
    name = 'ptac_apo_apo_12_26_12_26d'
    description = "MA(C,fast)−MA(C,slow)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/apo.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'mamode': 'sma', 'talib': False, 'offset': 0}；只输出'APO_12_26'；原目录：apo（fast=12, slow=26, mamode='sma'）；追踪：PF01178；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
