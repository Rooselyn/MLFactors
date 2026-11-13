"""Pandas TA Classic

公式：EMA(AD,fast)−EMA(AD,slow)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/adosc.py#L16)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 3, 'slow': 10, 'talib': False, 'offset': 0}；只输出'ADOSC_3_10'；原目录：adosc（fast=3, slow=10）；追踪：PF01311；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'ptac_adosc_adosc_3_10_3_10d', 'root_function': 'f_f911bb38f8_adosc', 'required_inputs': ['high', 'low', 'close', 'volume', 'open_'], 'parameters': {'fast': 3, 'slow': 10, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'ADOSC_3_10', 'gate_bars': 1, 'kernel': 'kernel_5e91988a741a7728', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_adosc_adosc_3_10_3_10d', {})
class Factor_ptac_adosc_adosc_3_10_3_10d(PublicFactor):
    name = 'ptac_adosc_adosc_3_10_3_10d'
    description = "EMA(AD,fast)−EMA(AD,slow)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/adosc.py#L16)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 3, 'slow': 10, 'talib': False, 'offset': 0}；只输出'ADOSC_3_10'；原目录：adosc（fast=3, slow=10）；追踪：PF01311；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
