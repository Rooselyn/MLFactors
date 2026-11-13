"""Pandas TA Classic

公式：源码算子/递推链：输出=result；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/cycles/ht_dcperiod.py#L14)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'talib': False, 'offset': 0}；只输出'HT_DCPERIOD'；原目录：ht_dcperiod（原函数默认参数/显式周期）；追踪：PF01172；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_ht_dcperiod_ht_dcperiod_alld', 'root_function': 'f_826b4fa54e_ht_dcperiod', 'required_inputs': ['close'], 'parameters': {'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'HT_DCPERIOD', 'gate_bars': 1, 'kernel': 'kernel_71249067557bab12', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_ht_dcperiod_ht_dcperiod_alld', {})
class Factor_ptac_ht_dcperiod_ht_dcperiod_alld(PublicFactor):
    name = 'ptac_ht_dcperiod_ht_dcperiod_alld'
    description = "源码算子/递推链：输出=result；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/cycles/ht_dcperiod.py#L14)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'talib': False, 'offset': 0}；只输出'HT_DCPERIOD'；原目录：ht_dcperiod（原函数默认参数/显式周期）；追踪：PF01172；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
