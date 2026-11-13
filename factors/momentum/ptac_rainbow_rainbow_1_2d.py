"""Pandas TA Classic

公式：源码算子/递推链：输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/rainbow.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 2, 'offset': 0}；只输出'RAINBOW_1'；原目录：rainbow（length=2）；追踪：PF01240；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_rainbow_rainbow_1_2d', 'root_function': 'f_9f2190ea33_rainbow', 'required_inputs': ['close'], 'parameters': {'length': 2, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'RAINBOW_1', 'gate_bars': 20, 'kernel': 'kernel_a9dd543f9265cc66', 'engine': 'ptac', 'minimum': 20}

@register_factor
@fixed_factor('ptac_rainbow_rainbow_1_2d', {})
class Factor_ptac_rainbow_rainbow_1_2d(PublicFactor):
    name = 'ptac_rainbow_rainbow_1_2d'
    description = "源码算子/递推链：输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/rainbow.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 2, 'offset': 0}；只输出'RAINBOW_1'；原目录：rainbow（length=2）；追踪：PF01240；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
