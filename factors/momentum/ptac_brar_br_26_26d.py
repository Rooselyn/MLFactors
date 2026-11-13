"""Pandas TA Classic

公式：源码算子/递推链：high_open_range = high - open_；open_low_range = open_ - low；hcy = high - close.shift(drift)；cyl = close.shift(drift) - low；olr_sum = open_low_range.rolling(length).sum()；ar = scalar * degenerate_div(high_open_range.rolling(length).sum(), olr_sum)；cyl_sum = cyl.rolling(length).sum()；br = scalar * degenerate_div(hcy.rolling(length).sum(), cyl_sum)；输出=brardf；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/brar.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 26, 'scalar': 100, 'drift': 1, 'offset': 0}；只输出'BR_26'；原目录：brar（length=26, scalar=100）；追踪：PF01180；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_brar_br_26_26d', 'root_function': 'f_d1215b8451_brar', 'required_inputs': ['open_', 'high', 'low', 'close'], 'parameters': {'length': 26, 'scalar': 100, 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'BR_26', 'gate_bars': 1, 'kernel': 'kernel_28ae036448b36323', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_brar_br_26_26d', {})
class Factor_ptac_brar_br_26_26d(PublicFactor):
    name = 'ptac_brar_br_26_26d'
    description = "源码算子/递推链：high_open_range = high - open_；open_low_range = open_ - low；hcy = high - close.shift(drift)；cyl = close.shift(drift) - low；olr_sum = open_low_range.rolling(length).sum()；ar = scalar * degenerate_div(high_open_range.rolling(length).sum(), olr_sum)；cyl_sum = cyl.rolling(length).sum()；br = scalar * degenerate_div(hcy.rolling(length).sum(), cyl_sum)；输出=brardf；输出=None；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/brar.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 26, 'scalar': 100, 'drift': 1, 'offset': 0}；只输出'BR_26'；原目录：brar（length=26, scalar=100）；追踪：PF01180；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
