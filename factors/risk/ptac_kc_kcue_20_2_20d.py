"""Pandas TA Classic

公式：Middle=EMA(TP,n)或EMA(C,n)；Upper/Lower=Middle±k×ATR(atr_n)，具体价格口径按来源；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/kc.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 20, 'scalar': 2, 'mamode': 'ema', 'offset': 0}；只输出'KCUe_20_2'；原目录：kc（length=20, mamode='ema'）；追踪：PF01303；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_kc_kcue_20_2_20d', 'root_function': 'f_2c125bb6f2_kc', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'length': 20, 'scalar': 2, 'mamode': 'ema', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 2, 'output_label': 'KCUe_20_2', 'gate_bars': 1, 'kernel': 'kernel_97ec8e535fd7f652', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_kc_kcue_20_2_20d', {})
class Factor_ptac_kc_kcue_20_2_20d(PublicFactor):
    name = 'ptac_kc_kcue_20_2_20d'
    description = "Middle=EMA(TP,n)或EMA(C,n)；Upper/Lower=Middle±k×ATR(atr_n)，具体价格口径按来源；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/kc.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 20, 'scalar': 2, 'mamode': 'ema', 'offset': 0}；只输出'KCUe_20_2'；原目录：kc（length=20, mamode='ema'）；追踪：PF01303；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
