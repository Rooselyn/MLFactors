"""Pandas TA Classic

公式：Tenkan=(max(H,n1)+min(L,n1))/2；Kijun同式n2；SpanA=(Tenkan+Kijun)/2，SpanB同式n3；绘图前移和Chikou后移不能产生提前可知信号；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/ichimoku.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'tenkan': 9, 'kijun': 26, 'senkou': 52, 'include_chikou': False, 'offset': 0, 'append_span': False}；只输出'ITS_9'；原目录：ichimoku（tenkan=None, kijun=None, senkou=None, include_chikou=True, append_span=False）；追踪：PF01229；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_ichimoku_its_9_9_26_52d', 'root_function': 'f_854aa1603f_ichimoku', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'tenkan': 9, 'kijun': 26, 'senkou': 52, 'include_chikou': False, 'offset': 0, 'append_span': False}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 2, 'output_label': 'ITS_9', 'gate_bars': 52, 'kernel': 'kernel_e2238536395f3c44', 'engine': 'ptac', 'minimum': 52}

@register_factor
@fixed_factor('ptac_ichimoku_its_9_9_26_52d', {})
class Factor_ptac_ichimoku_its_9_9_26_52d(PublicFactor):
    name = 'ptac_ichimoku_its_9_9_26_52d'
    description = "Tenkan=(max(H,n1)+min(L,n1))/2；Kijun同式n2；SpanA=(Tenkan+Kijun)/2，SpanB同式n3；绘图前移和Chikou后移不能产生提前可知信号；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/ichimoku.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'tenkan': 9, 'kijun': 26, 'senkou': 52, 'include_chikou': False, 'offset': 0, 'append_span': False}；只输出'ITS_9'；原目录：ichimoku（tenkan=None, kijun=None, senkou=None, include_chikou=True, append_span=False）；追踪：PF01229；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
