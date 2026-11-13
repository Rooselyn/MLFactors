"""Pandas TA Classic

公式：源码算子/递推链：输出=result；denom = c * length * (c_arr[i] / result[i - 1]) ^ 4；denom = max(denom, 1e-10)；result[i] = result[i - 1] + (c_arr[i] - result[i - 1]) / denom；源码算子/递推链：输出=mcg_ds；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/mcgd.py#L28)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'offset': 0, 'c': 1}；只输出'MCGD_10'；原目录：mcgd（length=10）；追踪：PF01235；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_mcgd_mcgd_10_10_1d', 'root_function': 'f_bbcefca2b0_mcgd', 'required_inputs': ['close'], 'parameters': {'length': 10, 'offset': 0, 'c': 1}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'MCGD_10', 'gate_bars': 1, 'kernel': 'kernel_49294dbe80ebef9c', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_mcgd_mcgd_10_10_1d', {})
class Factor_ptac_mcgd_mcgd_10_10_1d(PublicFactor):
    name = 'ptac_mcgd_mcgd_10_10_1d'
    description = "源码算子/递推链：输出=result；denom = c * length * (c_arr[i] / result[i - 1]) ^ 4；denom = max(denom, 1e-10)；result[i] = result[i - 1] + (c_arr[i] - result[i - 1]) / denom；源码算子/递推链：输出=mcg_ds；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/mcgd.py#L28)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'offset': 0, 'c': 1}；只输出'MCGD_10'；原目录：mcgd（length=10）；追踪：PF01235；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
