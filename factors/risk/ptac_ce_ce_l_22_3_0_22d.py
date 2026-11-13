"""Pandas TA Classic

公式：源码算子/递推链：highest_high = high.rolling(length, min_periods=length).max()；lowest_low = low.rolling(length, min_periods=length).min()；ce_long = highest_high - atr_ * multiplier；ce_short = lowest_low + atr_ * multiplier；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/ce.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 22, 'multiplier': 3.0, 'mamode': None, 'offset': 0}；只输出'CE_L_22_3.0'；原目录：ce（length=22）；追踪：PF01298；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_ce_ce_l_22_3_0_22d', 'root_function': 'f_bb4984bc77_ce', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'length': 22, 'multiplier': 3.0, 'mamode': None, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'CE_L_22_3.0', 'gate_bars': 1, 'kernel': 'kernel_a844aec8159fa188', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_ce_ce_l_22_3_0_22d', {})
class Factor_ptac_ce_ce_l_22_3_0_22d(PublicFactor):
    name = 'ptac_ce_ce_l_22_3_0_22d'
    description = "源码算子/递推链：highest_high = high.rolling(length, min_periods=length).max()；lowest_low = low.rolling(length, min_periods=length).min()；ce_long = highest_high - atr_ * multiplier；ce_short = lowest_low + atr_ * multiplier；输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/ce.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 22, 'multiplier': 3.0, 'mamode': None, 'offset': 0}；只输出'CE_L_22_3.0'；原目录：ce（length=22）；追踪：PF01298；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
