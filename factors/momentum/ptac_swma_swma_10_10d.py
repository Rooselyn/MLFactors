"""Pandas TA Classic

公式：源码算子/递推链：swma = close.rolling(length, min_periods=length).apply(weights(triangle), raw=True)；输出=swma；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/swma.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'offset': 0}；只输出'SWMA_10'；原目录：swma（length=10）；追踪：PF01246；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_swma_swma_10_10d', 'root_function': 'f_b8435821e2_swma', 'required_inputs': ['close'], 'parameters': {'length': 10, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'SWMA_10', 'gate_bars': 1, 'kernel': 'kernel_ea334d6bc59811ec', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_swma_swma_10_10d', {})
class Factor_ptac_swma_swma_10_10d(PublicFactor):
    name = 'ptac_swma_swma_10_10d'
    description = "源码算子/递推链：swma = close.rolling(length, min_periods=length).apply(weights(triangle), raw=True)；输出=swma；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/swma.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'offset': 0}；只输出'SWMA_10'；原目录：swma（length=10）；追踪：PF01246；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
