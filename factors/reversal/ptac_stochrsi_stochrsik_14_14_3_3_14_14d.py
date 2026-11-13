"""Pandas TA Classic

公式：(RSI−min(RSI,n))/(max(RSI,n)−min(RSI,n))，再按K/D窗口平滑；是否乘100按来源；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/stochrsi.py#L50)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'rsi_length': 14, 'k': 3, 'd': 3, 'mamode': 'sma', 'talib': False, 'offset': 0}；只输出'STOCHRSIk_14_14_3_3'；原目录：stochrsi（length=14, mamode='sma'）；追踪：PF01214；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_stochrsi_stochrsik_14_14_3_3_14_14d', 'root_function': 'f_aa301ba798_stochrsi', 'required_inputs': ['close'], 'parameters': {'length': 14, 'rsi_length': 14, 'k': 3, 'd': 3, 'mamode': 'sma', 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'STOCHRSIk_14_14_3_3', 'gate_bars': 1, 'kernel': 'kernel_51ac2917510a2883', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_stochrsi_stochrsik_14_14_3_3_14_14d', {})
class Factor_ptac_stochrsi_stochrsik_14_14_3_3_14_14d(PublicFactor):
    name = 'ptac_stochrsi_stochrsik_14_14_3_3_14_14d'
    description = "(RSI−min(RSI,n))/(max(RSI,n)−min(RSI,n))，再按K/D窗口平滑；是否乘100按来源；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/stochrsi.py#L50)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'rsi_length': 14, 'k': 3, 'd': 3, 'mamode': 'sma', 'talib': False, 'offset': 0}；只输出'STOCHRSIk_14_14_3_3'；原目录：stochrsi（length=14, mamode='sma'）；追踪：PF01214；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
