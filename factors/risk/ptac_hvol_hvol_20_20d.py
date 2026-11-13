"""Pandas TA Classic

公式：源码算子/递推链：log_returns = log(close / close.shift(1))；hvol_ = 100 * log_returns.rolling(length).std(ddof=1) * sqrt(annualization)；输出=hvol_；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/hvol.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 20, 'annualization': 252, 'offset': 0}；只输出'HVOL_20'；原目录：hvol（length=20）；追踪：PF01301；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_hvol_hvol_20_20d', 'root_function': 'f_4152eb6e3a_hvol', 'required_inputs': ['close'], 'parameters': {'length': 20, 'annualization': 252, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'HVOL_20', 'gate_bars': 1, 'kernel': 'kernel_ecc0be14bc093993', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_hvol_hvol_20_20d', {})
class Factor_ptac_hvol_hvol_20_20d(PublicFactor):
    name = 'ptac_hvol_hvol_20_20d'
    description = "源码算子/递推链：log_returns = log(close / close.shift(1))；hvol_ = 100 * log_returns.rolling(length).std(ddof=1) * sqrt(annualization)；输出=hvol_；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/hvol.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 20, 'annualization': 252, 'offset': 0}；只输出'HVOL_20'；原目录：hvol（length=20）；追踪：PF01301；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
