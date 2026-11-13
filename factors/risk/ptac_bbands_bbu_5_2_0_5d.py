"""Pandas TA Classic

公式：M=MA(C,n)；Upper=M+k_upσ_n(C)；Lower=M−k_downσ_n(C)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/bbands.py#L48)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 5, 'std': 2.0, 'ddof': 0, 'mamode': 'sma', 'talib': False, 'offset': 0}；只输出'BBU_5_2.0'；原目录：bbands（length=5, mamode='sma', ddof=0）；追踪：PF01297；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_bbands_bbu_5_2_0_5d', 'root_function': 'f_80e0d8c861_bbands', 'required_inputs': ['close'], 'parameters': {'length': 5, 'std': 2.0, 'ddof': 0, 'mamode': 'sma', 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 2, 'output_label': 'BBU_5_2.0', 'gate_bars': 1, 'kernel': 'kernel_7751ecf157750b0f', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_bbands_bbu_5_2_0_5d', {})
class Factor_ptac_bbands_bbu_5_2_0_5d(PublicFactor):
    name = 'ptac_bbands_bbu_5_2_0_5d'
    description = "M=MA(C,n)；Upper=M+k_upσ_n(C)；Lower=M−k_downσ_n(C)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/bbands.py#L48)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 5, 'std': 2.0, 'ddof': 0, 'mamode': 'sma', 'talib': False, 'offset': 0}；只输出'BBU_5_2.0'；原目录：bbands（length=5, mamode='sma', ddof=0）；追踪：PF01297；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
