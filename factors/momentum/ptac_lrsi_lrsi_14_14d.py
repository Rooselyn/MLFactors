"""Pandas TA Classic

公式：源码算子/递推链：输出=(l0, l1, l2, l3)；l0[i] = (1 - gamma) * c_arr[i] + gamma * l0[i - 1]；l1[i] = -gamma * l0[i] + l0[i - 1] + gamma * l1[i - 1]；l2[i] = -gamma * l1[i] + l1[i - 1] + gamma * l2[i - 1]；l3[i] = -gamma * l2[i] + l2[i - 1] + gamma * l3[i - 1]；源码算子/递推链：cu += maximum(l0 - l1, 0)；cd += maximum(l1 - l0, 0)；cu += maximum(l1 - l2, 0)；cd += maximum(l2 - l1, 0)；cu += maximum(l2 - l3, 0)；cd += maximum(l3 - l2, 0)；denominator = cu + cd；lrsi = Series(100 * cu / denominator, index=close.index)；输出=lrsi；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/lrsi.py#L29)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'gamma': 0.5, 'offset': 0}；只输出'LRSI_14'；原目录：lrsi（length=14）；追踪：PF01193；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_lrsi_lrsi_14_14d', 'root_function': 'f_218dc74888_lrsi', 'required_inputs': ['close'], 'parameters': {'length': 14, 'gamma': 0.5, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'LRSI_14', 'gate_bars': 1, 'kernel': 'kernel_7d62725df3b3fb17', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_lrsi_lrsi_14_14d', {})
class Factor_ptac_lrsi_lrsi_14_14d(PublicFactor):
    name = 'ptac_lrsi_lrsi_14_14d'
    description = "源码算子/递推链：输出=(l0, l1, l2, l3)；l0[i] = (1 - gamma) * c_arr[i] + gamma * l0[i - 1]；l1[i] = -gamma * l0[i] + l0[i - 1] + gamma * l1[i - 1]；l2[i] = -gamma * l1[i] + l1[i - 1] + gamma * l2[i - 1]；l3[i] = -gamma * l2[i] + l2[i - 1] + gamma * l3[i - 1]；源码算子/递推链：cu += maximum(l0 - l1, 0)；cd += maximum(l1 - l0, 0)；cu += maximum(l1 - l2, 0)；cd += maximum(l2 - l1, 0)；cu += maximum(l2 - l3, 0)；cd += maximum(l3 - l2, 0)；denominator = cu + cd；lrsi = Series(100 * cu / denominator, index=close.index)；输出=lrsi；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/lrsi.py#L29)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'gamma': 0.5, 'offset': 0}；只输出'LRSI_14'；原目录：lrsi（length=14）；追踪：PF01193；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
