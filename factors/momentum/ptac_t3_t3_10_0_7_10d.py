"""Pandas TA Classic

公式：源码算子/递推链：输出=t3；输出=None；c1 = -a * a ^ 2；c2 = 3 * a ^ 2 + 3 * a ^ 3；c3 = -6 * a ^ 2 - 3 * a - 3 * a ^ 3；c4 = a ^ 3 + 3 * a ^ 2 + 3 * a + 1；t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/t3.py#L14)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'a': 0.7, 'talib': False, 'offset': 0}；只输出'T3_10_0.7'；原目录：t3（length=10）；追踪：PF01247；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_t3_t3_10_0_7_10d', 'root_function': 'f_66995b3fd3_t3', 'required_inputs': ['close'], 'parameters': {'length': 10, 'a': 0.7, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'T3_10_0.7', 'gate_bars': 1, 'kernel': 'kernel_d445b7b31b889dd6', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_t3_t3_10_0_7_10d', {})
class Factor_ptac_t3_t3_10_0_7_10d(PublicFactor):
    name = 'ptac_t3_t3_10_0_7_10d'
    description = "源码算子/递推链：输出=t3；输出=None；c1 = -a * a ^ 2；c2 = 3 * a ^ 2 + 3 * a ^ 3；c3 = -6 * a ^ 2 - 3 * a - 3 * a ^ 3；c4 = a ^ 3 + 3 * a ^ 2 + 3 * a + 1；t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/t3.py#L14)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'a': 0.7, 'talib': False, 'offset': 0}；只输出'T3_10_0.7'；原目录：t3（length=10）；追踪：PF01247；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
