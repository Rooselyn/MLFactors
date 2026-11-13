"""Pandas TA Classic

公式：Σ_{j=0}^{n−1}(n−j)C[t−j] / (n(n+1)/2)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/wma.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'asc': True, 'talib': False, 'offset': 0}；只输出'WMA_10'；原目录：wma（length=10）；追踪：PF01253；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_wma_wma_10_10d', 'root_function': 'f_16e372fda3_wma', 'required_inputs': ['close'], 'parameters': {'length': 10, 'asc': True, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'WMA_10', 'gate_bars': 1, 'kernel': 'kernel_71985e0bb2869004', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_wma_wma_10_10d', {})
class Factor_ptac_wma_wma_10_10d(PublicFactor):
    name = 'ptac_wma_wma_10_10d'
    description = "Σ_{j=0}^{n−1}(n−j)C[t−j] / (n(n+1)/2)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/wma.py#L13)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'asc': True, 'talib': False, 'offset': 0}；只输出'WMA_10'；原目录：wma（length=10）；追踪：PF01253；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
