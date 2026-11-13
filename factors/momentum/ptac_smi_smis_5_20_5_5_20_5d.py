"""Pandas TA Classic

公式：源码算子/递推链：osc = smi - signalma；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/smi.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 5, 'slow': 20, 'signal': 5, 'scalar': 1, 'offset': 0}；只输出'SMIs_5_20_5'；原目录：smi（fast=5, slow=20, signal=5, scalar=1）；追踪：PF01208；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_smi_smis_5_20_5_5_20_5d', 'root_function': 'f_778520b72d_smi', 'required_inputs': ['close'], 'parameters': {'fast': 5, 'slow': 20, 'signal': 5, 'scalar': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'SMIs_5_20_5', 'gate_bars': 1, 'kernel': 'kernel_36ddff72b66710a5', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_smi_smis_5_20_5_5_20_5d', {})
class Factor_ptac_smi_smis_5_20_5_5_20_5d(PublicFactor):
    name = 'ptac_smi_smis_5_20_5_5_20_5d'
    description = "源码算子/递推链：osc = smi - signalma；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/smi.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 5, 'slow': 20, 'signal': 5, 'scalar': 1, 'offset': 0}；只输出'SMIs_5_20_5'；原目录：smi（fast=5, slow=20, signal=5, scalar=1）；追踪：PF01208；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
