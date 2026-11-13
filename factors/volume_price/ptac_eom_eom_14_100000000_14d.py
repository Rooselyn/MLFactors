"""Pandas TA Classic

公式：源码算子/递推链：high_low_range = high - low；distance -= hl2(high=high.shift(drift), low=low.shift(drift))；box_ratio = volume / divisor；box_ratio /= high_low_range.where(high_low_range != 0)；eom = (distance / box_ratio).mask(high_low_range == 0, 0.0)；输出=eom；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/eom.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'divisor': 100000000, 'drift': 1, 'offset': 0}；只输出'EOM_14_100000000'；原目录：eom（length=14）；追踪：PF01315；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_eom_eom_14_100000000_14d', 'root_function': 'f_19c734cf68_eom', 'required_inputs': ['high', 'low', 'close', 'volume'], 'parameters': {'length': 14, 'divisor': 100000000, 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'EOM_14_100000000', 'gate_bars': 1, 'kernel': 'kernel_02ca48dbaba8f631', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_eom_eom_14_100000000_14d', {})
class Factor_ptac_eom_eom_14_100000000_14d(PublicFactor):
    name = 'ptac_eom_eom_14_100000000_14d'
    description = "源码算子/递推链：high_low_range = high - low；distance -= hl2(high=high.shift(drift), low=low.shift(drift))；box_ratio = volume / divisor；box_ratio /= high_low_range.where(high_low_range != 0)；eom = (distance / box_ratio).mask(high_low_range == 0, 0.0)；输出=eom；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/eom.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'divisor': 100000000, 'drift': 1, 'offset': 0}；只输出'EOM_14_100000000'；原目录：eom（length=14）；追踪：PF01315；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
