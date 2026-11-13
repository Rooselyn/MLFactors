"""Pandas TA Classic

公式：(max(C,n)+min(C,n))/2；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/midpoint.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 2, 'talib': False, 'offset': 0}；只输出'MIDPOINT_2'；原目录：midpoint（length=2）；追踪：PF01236；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_midpoint_midpoint_2_2d', 'root_function': 'f_50ba6a70c4_midpoint', 'required_inputs': ['close'], 'parameters': {'length': 2, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'MIDPOINT_2', 'gate_bars': 1, 'kernel': 'kernel_69983f908f8824cd', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_midpoint_midpoint_2_2d', {})
class Factor_ptac_midpoint_midpoint_2_2d(PublicFactor):
    name = 'ptac_midpoint_midpoint_2_2d'
    description = "(max(C,n)+min(C,n))/2；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/midpoint.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 2, 'talib': False, 'offset': 0}；只输出'MIDPOINT_2'；原目录：midpoint（length=2）；追踪：PF01236；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
