"""Pandas TA Classic

公式：源码算子/递推链：highest_close = close.rolling(length).max()；downside = scalar * (close - highest_close)；downside /= highest_close；d2 = downside * downside；输出=ui；输出=None；ui = (sma(d2, length) / length).apply(sqrt)；ui = (d2.rolling(length).sum() / length).apply(sqrt)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/ui.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'scalar': 100, 'offset': 0}；只输出'UI_14'；原目录：ui（length=14）；追踪：PF01309；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_ui_ui_14_14d', 'root_function': 'f_996ab5a43e_ui', 'required_inputs': ['close'], 'parameters': {'length': 14, 'scalar': 100, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'UI_14', 'gate_bars': 1, 'kernel': 'kernel_f5e9db9cca1fd107', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_ui_ui_14_14d', {})
class Factor_ptac_ui_ui_14_14d(PublicFactor):
    name = 'ptac_ui_ui_14_14d'
    description = "源码算子/递推链：highest_close = close.rolling(length).max()；downside = scalar * (close - highest_close)；downside /= highest_close；d2 = downside * downside；输出=ui；输出=None；ui = (sma(d2, length) / length).apply(sqrt)；ui = (d2.rolling(length).sum() / length).apply(sqrt)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volatility/ui.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'scalar': 100, 'offset': 0}；只输出'UI_14'；原目录：ui（length=14）；追踪：PF01309；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
