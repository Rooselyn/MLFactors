"""Pandas TA Classic

公式：FastK=100(C−min(L,n))/(max(H,n)−min(L,n))；FastD=MA(FastK,d)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/stochf.py#L43)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fastk': 5, 'fastd': 3, 'mamode': 'sma', 'talib': False, 'offset': 0}；只输出'STOCHFk_5_3'；原目录：stochf（mamode='sma'）；追踪：PF01213；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_stochf_stochfk_5_3_5_3d', 'root_function': 'f_fd0245ff34_stochf', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'fastk': 5, 'fastd': 3, 'mamode': 'sma', 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'STOCHFk_5_3', 'gate_bars': 1, 'kernel': 'kernel_56aa2221a769d45b', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_stochf_stochfk_5_3_5_3d', {})
class Factor_ptac_stochf_stochfk_5_3_5_3d(PublicFactor):
    name = 'ptac_stochf_stochfk_5_3_5_3d'
    description = "FastK=100(C−min(L,n))/(max(H,n)−min(L,n))；FastD=MA(FastK,d)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/stochf.py#L43)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fastk': 5, 'fastd': 3, 'mamode': 'sma', 'talib': False, 'offset': 0}；只输出'STOCHFk_5_3'；原目录：stochf（mamode='sma'）；追踪：PF01213；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
