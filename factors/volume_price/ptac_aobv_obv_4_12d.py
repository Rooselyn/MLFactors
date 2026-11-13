"""Pandas TA Classic

公式：源码算子/递推链：obv_min = obv_.rolling(min_lookback).min()；obv_max = obv_.rolling(max_lookback).max()；输出=aobvdf；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/aobv.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 4, 'slow': 12, 'max_lookback': 2, 'min_lookback': 2, 'mamode': 'ema', 'offset': 0}；只输出'OBV'；原目录：aobv（fast=4, slow=12, mamode='ema'）；追踪：PF01312；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_aobv_obv_4_12d', 'root_function': 'f_4c3a20af7d_aobv', 'required_inputs': ['close', 'volume'], 'parameters': {'fast': 4, 'slow': 12, 'max_lookback': 2, 'min_lookback': 2, 'mamode': 'ema', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'OBV', 'gate_bars': 1, 'kernel': 'kernel_725f08639ef6ff14', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_aobv_obv_4_12d', {})
class Factor_ptac_aobv_obv_4_12d(PublicFactor):
    name = 'ptac_aobv_obv_4_12d'
    description = "源码算子/递推链：obv_min = obv_.rolling(min_lookback).min()；obv_max = obv_.rolling(max_lookback).max()；输出=aobvdf；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/aobv.py#L17)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 4, 'slow': 12, 'max_lookback': 2, 'min_lookback': 2, 'mamode': 'ema', 'offset': 0}；只输出'OBV'；原目录：aobv（fast=4, slow=12, mamode='ema'）；追踪：PF01312；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
