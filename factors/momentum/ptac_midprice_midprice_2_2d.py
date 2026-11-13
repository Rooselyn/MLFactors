"""Pandas TA Classic

公式：(max(H,n)+min(L,n))/2；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/midprice.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 2, 'talib': False, 'offset': 0}；只输出'MIDPRICE_2'；原目录：midprice（length=2）；追踪：PF01237；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'ptac_midprice_midprice_2_2d', 'root_function': 'f_9266fc8e84_midprice', 'required_inputs': ['high', 'low'], 'parameters': {'length': 2, 'talib': False, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'MIDPRICE_2', 'gate_bars': 1, 'kernel': 'kernel_2681c820aa018c8a', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_midprice_midprice_2_2d', {})
class Factor_ptac_midprice_midprice_2_2d(PublicFactor):
    name = 'ptac_midprice_midprice_2_2d'
    description = "(max(H,n)+min(L,n))/2；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/midprice.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 2, 'talib': False, 'offset': 0}；只输出'MIDPRICE_2'；原目录：midprice（length=2）；追踪：PF01237；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
