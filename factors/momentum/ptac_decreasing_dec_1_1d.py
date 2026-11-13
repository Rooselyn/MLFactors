"""Pandas TA Classic

公式：源码算子/递推链：close_ = (1 - 0.01 * percent) * close if percent else close；_percent = f'_{0.01 * percent}' if percent else ''；输出=decreasing；输出=None；decreasing = close < close_.shift(drift)；decreasing = close_.diff(length) < 0；decreasing = decreasing & (close.shift(x - (drift + 1)) < close_.shift(x - drift))；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/decreasing.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 1, 'strict': False, 'asint': True, 'percent': None, 'drift': 1, 'offset': 0}；只输出'DEC_1'；原目录：decreasing（length=1）；追踪：PF01276；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_decreasing_dec_1_1d', 'root_function': 'f_8bfdea6eee_decreasing', 'required_inputs': ['close'], 'parameters': {'length': 1, 'strict': False, 'asint': True, 'percent': None, 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'DEC_1', 'gate_bars': 1, 'kernel': 'kernel_e113cbe6779103a2', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_decreasing_dec_1_1d', {})
class Factor_ptac_decreasing_dec_1_1d(PublicFactor):
    name = 'ptac_decreasing_dec_1_1d'
    description = "源码算子/递推链：close_ = (1 - 0.01 * percent) * close if percent else close；_percent = f'_{0.01 * percent}' if percent else ''；输出=decreasing；输出=None；decreasing = close < close_.shift(drift)；decreasing = close_.diff(length) < 0；decreasing = decreasing & (close.shift(x - (drift + 1)) < close_.shift(x - drift))；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/trend/decreasing.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 1, 'strict': False, 'asint': True, 'percent': None, 'drift': 1, 'offset': 0}；只输出'DEC_1'；原目录：decreasing（length=1）；追踪：PF01276；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
