"""Pandas TA Classic

公式：源码算子/递推链：slope = close.diff(length) / length；输出=slope；输出=None；slope *= 180 / pi；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/slope.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 1, 'as_angle': False, 'to_degrees': False, 'offset': 0}；只输出'SLOPE_1'；原目录：slope（length=1）；追踪：PF01206；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_slope_slope_1_1d', 'root_function': 'f_76764ec186_slope', 'required_inputs': ['close'], 'parameters': {'length': 1, 'as_angle': False, 'to_degrees': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'SLOPE_1', 'gate_bars': 1, 'kernel': 'kernel_84186fb2c2d0a39a', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_slope_slope_1_1d', {})
class Factor_ptac_slope_slope_1_1d(PublicFactor):
    name = 'ptac_slope_slope_1_1d'
    description = "源码算子/递推链：slope = close.diff(length) / length；输出=slope；输出=None；slope *= 180 / pi；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/slope.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 1, 'as_angle': False, 'to_degrees': False, 'offset': 0}；只输出'SLOPE_1'；原目录：slope（length=1）；追踪：PF01206；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
