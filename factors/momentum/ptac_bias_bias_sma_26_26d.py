"""Pandas TA Classic

公式：源码算子/递推链：bias = close / bma - 1；输出=bias；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/bias.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 26, 'mamode': 'sma', 'offset': 0}；只输出'BIAS_SMA_26'；原目录：bias（length=26, mamode='sma'）；追踪：PF01179；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_bias_bias_sma_26_26d', 'root_function': 'f_c620d44690_bias', 'required_inputs': ['close'], 'parameters': {'length': 26, 'mamode': 'sma', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'BIAS_SMA_26', 'gate_bars': 1, 'kernel': 'kernel_3b4d700400df2145', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_bias_bias_sma_26_26d', {})
class Factor_ptac_bias_bias_sma_26_26d(PublicFactor):
    name = 'ptac_bias_bias_sma_26_26d'
    description = "源码算子/递推链：bias = close / bma - 1；输出=bias；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/bias.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 26, 'mamode': 'sma', 'offset': 0}；只输出'BIAS_SMA_26'；原目录：bias（length=26, mamode='sma'）；追踪：PF01179；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
