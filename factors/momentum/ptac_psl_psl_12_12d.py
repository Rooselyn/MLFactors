"""Pandas TA Classic

公式：源码算子/递推链：psl = scalar * diff.rolling(length).sum()；psl /= length；输出=psl；输出=None；diff = sign(close - open_)；diff = sign(close.diff(drift))；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/psl.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 12, 'scalar': 100, 'drift': 1, 'offset': 0}；只输出'PSL_12'；原目录：psl（length=12）；追踪：PF01200；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'ptac_psl_psl_12_12d', 'root_function': 'f_6fa51a7b2c_psl', 'required_inputs': ['close', 'open_'], 'parameters': {'length': 12, 'scalar': 100, 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'PSL_12', 'gate_bars': 1, 'kernel': 'kernel_115c7fb0fec0ef9b', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_psl_psl_12_12d', {})
class Factor_ptac_psl_psl_12_12d(PublicFactor):
    name = 'ptac_psl_psl_12_12d'
    description = "源码算子/递推链：psl = scalar * diff.rolling(length).sum()；psl /= length；输出=psl；输出=None；diff = sign(close - open_)；diff = sign(close.diff(drift))；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/psl.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 12, 'scalar': 100, 'drift': 1, 'offset': 0}；只输出'PSL_12'；原目录：psl（length=12）；追踪：PF01200；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
