"""Pandas TA Classic

公式：源码算子/递推链：dsp = close - ema_value；输出=dsp；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/cycles/dsp.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'offset': 0}；只输出'DSP_14'；原目录：dsp（length=14）；追踪：PF01170；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_dsp_dsp_14_14d', 'root_function': 'f_db796af3a4_dsp', 'required_inputs': ['close'], 'parameters': {'length': 14, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'DSP_14', 'gate_bars': 1, 'kernel': 'kernel_89f1b75d8892be4c', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_dsp_dsp_14_14d', {})
class Factor_ptac_dsp_dsp_14_14d(PublicFactor):
    name = 'ptac_dsp_dsp_14_14d'
    description = "源码算子/递推链：dsp = close - ema_value；输出=dsp；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/cycles/dsp.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'offset': 0}；只输出'DSP_14'；原目录：dsp（length=14）；追踪：PF01170；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
