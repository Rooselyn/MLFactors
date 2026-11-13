"""Pandas TA Classic

公式：源码算子/递推链：vosc_ = 100 * (fast_sma - slow_sma) / slow_sma；输出=vosc_；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/vosc.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 14, 'slow': 28, 'offset': 0}；只输出'VOSC_14_28'；原目录：vosc（fast=14, slow=28）；追踪：PF01324；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_vosc_vosc_14_28_14_28d', 'root_function': 'f_78a3c494fa_vosc', 'required_inputs': ['volume'], 'parameters': {'fast': 14, 'slow': 28, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'VOSC_14_28', 'gate_bars': 1, 'kernel': 'kernel_f6efef4872cbf06a', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_vosc_vosc_14_28_14_28d', {})
class Factor_ptac_vosc_vosc_14_28_14_28d(PublicFactor):
    name = 'ptac_vosc_vosc_14_28_14_28d'
    description = "源码算子/递推链：vosc_ = 100 * (fast_sma - slow_sma) / slow_sma；输出=vosc_；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/vosc.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 14, 'slow': 28, 'offset': 0}；只输出'VOSC_14_28'；原目录：vosc（fast=14, slow=28）；追踪：PF01324；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
