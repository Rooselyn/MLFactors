"""Pandas TA Classic

公式：源码算子/递推链：histogram = trix_line - trix_signal；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/trixh.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 18, 'signal': 9, 'scalar': 100, 'drift': None, 'offset': 0}；只输出'TRIXh_18_9'；原目录：trixh（length=18, signal=9, scalar=100）；追踪：PF01217；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_trixh_trixh_18_9_18_9d', 'root_function': 'f_5fe8ee83a2_trixh', 'required_inputs': ['close'], 'parameters': {'length': 18, 'signal': 9, 'scalar': 100, 'drift': None, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 2, 'output_label': 'TRIXh_18_9', 'gate_bars': 1, 'kernel': 'kernel_d4f8200edc3fe2bd', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_trixh_trixh_18_9_18_9d', {})
class Factor_ptac_trixh_trixh_18_9_18_9d(PublicFactor):
    name = 'ptac_trixh_trixh_18_9_18_9d'
    description = "源码算子/递推链：histogram = trix_line - trix_signal；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/trixh.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 18, 'signal': 9, 'scalar': 100, 'drift': None, 'offset': 0}；只输出'TRIXh_18_9'；原目录：trixh（length=18, signal=9, scalar=100）；追踪：PF01217；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
