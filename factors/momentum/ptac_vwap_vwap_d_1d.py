"""Pandas TA Classic

公式：典型价格TP=(H+L+C)/3；sum(TP×V)/sum(V)，按来源的滚动或会话锚定；不等于实际amount/vol；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/vwap.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'anchor': 'D', 'offset': 0}；只输出'VWAP_D'；原目录：vwap（anchor=None）；追踪：PF01251；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_vwap_vwap_d_1d', 'root_function': 'f_7c8b82acfc_vwap', 'required_inputs': ['high', 'low', 'close', 'volume'], 'parameters': {'anchor': 'D', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'VWAP_D', 'gate_bars': 1, 'kernel': 'kernel_deb00b4728515fd9', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_vwap_vwap_d_1d', {})
class Factor_ptac_vwap_vwap_d_1d(PublicFactor):
    name = 'ptac_vwap_vwap_d_1d'
    description = "典型价格TP=(H+L+C)/3；sum(TP×V)/sum(V)，按来源的滚动或会话锚定；不等于实际amount/vol；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/vwap.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'anchor': 'D', 'offset': 0}；只输出'VWAP_D'；原目录：vwap（anchor=None）；追踪：PF01251；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
