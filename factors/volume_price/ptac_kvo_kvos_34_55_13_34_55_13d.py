"""Pandas TA Classic

公式：源码算子/递推链：signed_volume = volume * signed_series(hlc3(high, low, close))；kvo = _kvo_fast - _kvo_slow；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/kvo.py#L20)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 34, 'slow': 55, 'signal': 13, 'mamode': 'ema', 'offset': 0}；只输出'KVOs_34_55_13'；原目录：kvo（fast=34, slow=55, signal=13, mamode='ema'）；追踪：PF01316；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_kvo_kvos_34_55_13_34_55_13d', 'root_function': 'f_a007ecde8a_kvo', 'required_inputs': ['high', 'low', 'close', 'volume'], 'parameters': {'fast': 34, 'slow': 55, 'signal': 13, 'mamode': 'ema', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'KVOs_34_55_13', 'gate_bars': 68, 'kernel': 'kernel_da6523694101524b', 'engine': 'ptac', 'minimum': 68}

@register_factor
@fixed_factor('ptac_kvo_kvos_34_55_13_34_55_13d', {})
class Factor_ptac_kvo_kvos_34_55_13_34_55_13d(PublicFactor):
    name = 'ptac_kvo_kvos_34_55_13_34_55_13d'
    description = "源码算子/递推链：signed_volume = volume * signed_series(hlc3(high, low, close))；kvo = _kvo_fast - _kvo_slow；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/kvo.py#L20)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 34, 'slow': 55, 'signal': 13, 'mamode': 'ema', 'offset': 0}；只输出'KVOs_34_55_13'；原目录：kvo（fast=34, slow=55, signal=13, mamode='ema'）；追踪：PF01316；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
