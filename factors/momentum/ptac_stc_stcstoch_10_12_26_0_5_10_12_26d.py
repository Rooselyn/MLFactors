"""Pandas TA Classic

公式：源码算子/递推链：输出=fastma - slowma；输出=osc；输出=ma1 - ma2；输出=None；源码算子/递推链：输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/stc.py#L99)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'tclength': 10, 'fast': 12, 'slow': 26, 'factor': 0.5, 'offset': 0}；只输出'STCstoch_10_12_26_0.5'；原目录：stc（fast=12, slow=26）；追踪：PF01211；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_stc_stcstoch_10_12_26_0_5_10_12_26d', 'root_function': 'f_f6ba64db3a_stc', 'required_inputs': ['close'], 'parameters': {'tclength': 10, 'fast': 12, 'slow': 26, 'factor': 0.5, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 2, 'output_label': 'STCstoch_10_12_26_0.5', 'gate_bars': 26, 'kernel': 'kernel_27236ee31cdfcf46', 'engine': 'ptac', 'minimum': 26}

@register_factor
@fixed_factor('ptac_stc_stcstoch_10_12_26_0_5_10_12_26d', {})
class Factor_ptac_stc_stcstoch_10_12_26_0_5_10_12_26d(PublicFactor):
    name = 'ptac_stc_stcstoch_10_12_26_0_5_10_12_26d'
    description = "源码算子/递推链：输出=fastma - slowma；输出=osc；输出=ma1 - ma2；输出=None；源码算子/递推链：输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/stc.py#L99)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'tclength': 10, 'fast': 12, 'slow': 26, 'factor': 0.5, 'offset': 0}；只输出'STCstoch_10_12_26_0.5'；原目录：stc（fast=12, slow=26）；追踪：PF01211；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
