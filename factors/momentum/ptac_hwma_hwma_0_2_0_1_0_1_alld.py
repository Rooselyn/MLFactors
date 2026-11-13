"""Pandas TA Classic

公式：源码算子/递推链：输出=result；F = (1.0 - na) * (last_f + last_v + 0.5 * last_a) + na * c_arr[i]；V = (1.0 - nb) * (last_v + last_a) + nb * (F - last_f)；A = (1.0 - nc) * last_a + nc * (V - last_v)；result[i] = F + V + 0.5 * A；源码算子/递推链：输出=hwma；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/hwma.py#L31)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'na': 0.2, 'nb': 0.1, 'nc': 0.1, 'offset': 0}；只输出'HWMA_0.2_0.1_0.1'；原目录：hwma（na=None, nb=None, nc=None）；追踪：PF01228；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_hwma_hwma_0_2_0_1_0_1_alld', 'root_function': 'f_7ac7e7fe8a_hwma', 'required_inputs': ['close'], 'parameters': {'na': 0.2, 'nb': 0.1, 'nc': 0.1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'HWMA_0.2_0.1_0.1', 'gate_bars': 1, 'kernel': 'kernel_86c98c9d7e37cb4e', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_hwma_hwma_0_2_0_1_0_1_alld', {})
class Factor_ptac_hwma_hwma_0_2_0_1_0_1_alld(PublicFactor):
    name = 'ptac_hwma_hwma_0_2_0_1_0_1_alld'
    description = "源码算子/递推链：输出=result；F = (1.0 - na) * (last_f + last_v + 0.5 * last_a) + na * c_arr[i]；V = (1.0 - nb) * (last_v + last_a) + nb * (F - last_f)；A = (1.0 - nc) * last_a + nc * (V - last_v)；result[i] = F + V + 0.5 * A；源码算子/递推链：输出=hwma；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/hwma.py#L31)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'na': 0.2, 'nb': 0.1, 'nc': 0.1, 'offset': 0}；只输出'HWMA_0.2_0.1_0.1'；原目录：hwma（na=None, nb=None, nc=None）；追踪：PF01228；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
