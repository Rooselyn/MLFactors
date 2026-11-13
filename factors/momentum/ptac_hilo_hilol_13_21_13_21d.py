"""Pandas TA Classic

公式：源码算子/递推链：输出=(hilo, long, short)；hilo[i] = hilo[i - 1]；long[i] = hilo[i - 1]；short[i] = hilo[i - 1]；源码算子/递推链：输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/hilo.py#L40)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'high_length': 13, 'low_length': 21, 'mamode': 'sma', 'offset': 0}；只输出'HILOl_13_21'；原目录：hilo（mamode='sma'）；追踪：PF01225；[来源](https://github.com/xgboosted/pandas-ta-classic)。
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
SPEC = {'name': 'ptac_hilo_hilol_13_21_13_21d', 'root_function': 'f_f6ef840fa3_hilo', 'required_inputs': ['high', 'low', 'close'], 'parameters': {'high_length': 13, 'low_length': 21, 'mamode': 'sma', 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'HILOl_13_21', 'gate_bars': 1, 'kernel': 'kernel_a2b7f6a218e24ed0', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_hilo_hilol_13_21_13_21d', {})
class Factor_ptac_hilo_hilol_13_21_13_21d(PublicFactor):
    name = 'ptac_hilo_hilol_13_21_13_21d'
    description = "源码算子/递推链：输出=(hilo, long, short)；hilo[i] = hilo[i - 1]；long[i] = hilo[i - 1]；short[i] = hilo[i - 1]；源码算子/递推链：输出=df；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/hilo.py#L40)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'high_length': 13, 'low_length': 21, 'mamode': 'sma', 'offset': 0}；只输出'HILOl_13_21'；原目录：hilo（mamode='sma'）；追踪：PF01225；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
