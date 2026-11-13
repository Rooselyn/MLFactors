"""Pandas TA Classic

公式：源码算子/递推链：输出=ssf_arr；ssf_arr[i] = c1 * c_arr[i] + b1 * ssf_arr[i - 1] + a1 * ssf_arr[i - 2]；源码算子/递推链：输出=ssf_arr；ssf_arr[i] = c1 * c_arr[i] + c2 * ssf_arr[i - 1] + c3 * ssf_arr[i - 2] + c4 * ssf_arr[i - 3]；源码算子/递推链：输出=ssf；输出=None；x = pi / length；a0 = exp(-x)；b0 = 2 * a0 * cos(sqrt(3) * x)；c0 = a0 * a0；c4 = c0 * c0；c3 = -c0 * (1 + b0)；c2 = c0 + b0；c1 = 1 - c2 - c3 - c4；x = pi * sqrt(2) / length；a1 = -a0 * a0；b1 = 2 * a0 * cos(x)；c1 = 1 - a1 - b1；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/ssf.py#L28)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'poles': 2, 'offset': 0}；只输出'SSF_10_2'；原目录：ssf（length=10）；追踪：PF01244；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_ssf_ssf_10_2_10d', 'root_function': 'f_de4dfe058b_ssf', 'required_inputs': ['close'], 'parameters': {'length': 10, 'poles': 2, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'SSF_10_2', 'gate_bars': 1, 'kernel': 'kernel_d5d39db50cdc92a8', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_ssf_ssf_10_2_10d', {})
class Factor_ptac_ssf_ssf_10_2_10d(PublicFactor):
    name = 'ptac_ssf_ssf_10_2_10d'
    description = "源码算子/递推链：输出=ssf_arr；ssf_arr[i] = c1 * c_arr[i] + b1 * ssf_arr[i - 1] + a1 * ssf_arr[i - 2]；源码算子/递推链：输出=ssf_arr；ssf_arr[i] = c1 * c_arr[i] + c2 * ssf_arr[i - 1] + c3 * ssf_arr[i - 2] + c4 * ssf_arr[i - 3]；源码算子/递推链：输出=ssf；输出=None；x = pi / length；a0 = exp(-x)；b0 = 2 * a0 * cos(sqrt(3) * x)；c0 = a0 * a0；c4 = c0 * c0；c3 = -c0 * (1 + b0)；c2 = c0 + b0；c1 = 1 - c2 - c3 - c4；x = pi * sqrt(2) / length；a1 = -a0 * a0；b1 = 2 * a0 * cos(x)；c1 = 1 - a1 - b1；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/ssf.py#L28)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'poles': 2, 'offset': 0}；只输出'SSF_10_2'；原目录：ssf（length=10）；追踪：PF01244；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
