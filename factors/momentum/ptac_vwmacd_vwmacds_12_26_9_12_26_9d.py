"""Pandas TA Classic

公式：源码算子/递推链：vwmacd = fast_vwma - slow_vwma；histogram = vwmacd - signal_line；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/vwmacd.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'signal': 9, 'offset': 0}；只输出'VWMACDs_12_26_9'；原目录：vwmacd（fast=12, slow=26, signal=9）；追踪：PF01220；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_vwmacd_vwmacds_12_26_9_12_26_9d', 'root_function': 'f_10c450b5ba_vwmacd', 'required_inputs': ['close', 'volume'], 'parameters': {'fast': 12, 'slow': 26, 'signal': 9, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 2, 'output_label': 'VWMACDs_12_26_9', 'gate_bars': 1, 'kernel': 'kernel_1c74571874dce617', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_vwmacd_vwmacds_12_26_9_12_26_9d', {})
class Factor_ptac_vwmacd_vwmacds_12_26_9_12_26_9d(PublicFactor):
    name = 'ptac_vwmacd_vwmacds_12_26_9_12_26_9d'
    description = "源码算子/递推链：vwmacd = fast_vwma - slow_vwma；histogram = vwmacd - signal_line；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/vwmacd.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'signal': 9, 'offset': 0}；只输出'VWMACDs_12_26_9'；原目录：vwmacd（fast=12, slow=26, signal=9）；追踪：PF01220；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
