"""Pandas TA Classic

公式：源码算子/递推链：result[length - 1] = 0.0；输出=result；f88 = length - 1.0 if length - 1.0 >= 5 else 5.0；f8 = 100.0 * c_arr[i]；f18 = 3.0 / (length + 2.0)；f20 = 1.0 - f18；f90 = f88 + 1 if f88 <= f90 else f90 + 1；v8 = f8 - f10；f28 = f20 * f28 + f18 * v8；f30 = f18 * f28 + f20 * f30；vC = 1.5 * f28 - 0.5 * f30；f38 = f20 * f38 + f18 * vC；f40 = f18 * f38 + f20 * f40；v10 = 1.5 * f38 - 0.5 * f40；f48 = f20 * f48 + f18 * v10；f50 = f18 * f48 + f20 * f50；v14 = 1.5 * f48 - 0.5 * f50；f58 = f20 * f58 + f18 * abs(v8)；f60 = f18 * f58 + f20 * f60；v18 = 1.5 * f58 - 0.5 * f60；f68 = f20 * f68 + f18 * v18；f70 = f18 * f68 + f20 * f70；v1C = 1.5 * f68 - 0.5 * f70；f78 = f20 * f78 + f18 * v1C；源码算子/递推链：输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/rsx.py#L67)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'offset': 0}；只输出'RSX_14'；原目录：rsx（length=14）；追踪：PF01204；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_rsx_rsx_14_14d', 'root_function': 'f_acd45b3fd9_rsx', 'required_inputs': ['close'], 'parameters': {'length': 14, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'RSX_14', 'gate_bars': 1, 'kernel': 'kernel_29b0af645d1be59d', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_rsx_rsx_14_14d', {})
class Factor_ptac_rsx_rsx_14_14d(PublicFactor):
    name = 'ptac_rsx_rsx_14_14d'
    description = "源码算子/递推链：result[length - 1] = 0.0；输出=result；f88 = length - 1.0 if length - 1.0 >= 5 else 5.0；f8 = 100.0 * c_arr[i]；f18 = 3.0 / (length + 2.0)；f20 = 1.0 - f18；f90 = f88 + 1 if f88 <= f90 else f90 + 1；v8 = f8 - f10；f28 = f20 * f28 + f18 * v8；f30 = f18 * f28 + f20 * f30；vC = 1.5 * f28 - 0.5 * f30；f38 = f20 * f38 + f18 * vC；f40 = f18 * f38 + f20 * f40；v10 = 1.5 * f38 - 0.5 * f40；f48 = f20 * f48 + f18 * v10；f50 = f18 * f48 + f20 * f50；v14 = 1.5 * f48 - 0.5 * f50；f58 = f20 * f58 + f18 * abs(v8)；f60 = f18 * f58 + f20 * f60；v18 = 1.5 * f58 - 0.5 * f60；f68 = f20 * f68 + f18 * v18；f70 = f18 * f68 + f20 * f70；v1C = 1.5 * f68 - 0.5 * f70；f78 = f20 * f78 + f18 * v1C；源码算子/递推链：输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/rsx.py#L67)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'offset': 0}；只输出'RSX_14'；原目录：rsx（length=14）；追踪：PF01204；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
