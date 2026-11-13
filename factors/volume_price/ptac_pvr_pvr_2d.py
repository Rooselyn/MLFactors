"""Pandas TA Classic

公式：源码算子/递推链：close_diff = close.diff()；volume_diff = volume.diff()；输出=pvr_；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/pvr.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'offset': 0}；只输出'PVR'；原目录：pvr（原函数默认参数/显式周期）；追踪：PF01321；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_pvr_pvr_2d', 'root_function': 'f_2dfd5b13bb_pvr', 'required_inputs': ['close', 'volume'], 'parameters': {'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'PVR', 'gate_bars': 1, 'kernel': 'kernel_cf56791b15c16f7c', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_pvr_pvr_2d', {})
class Factor_ptac_pvr_pvr_2d(PublicFactor):
    name = 'ptac_pvr_pvr_2d'
    description = "源码算子/递推链：close_diff = close.diff()；volume_diff = volume.diff()；输出=pvr_；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/pvr.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'offset': 0}；只输出'PVR'；原目录：pvr（原函数默认参数/显式周期）；追踪：PF01321；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
