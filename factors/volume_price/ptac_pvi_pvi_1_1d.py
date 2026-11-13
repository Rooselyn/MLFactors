"""Pandas TA Classic

公式：PVI_t=PVI_{t−1}×(1+R_t)若V_t>V_{t−1}，否则保持；初值按来源；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/pvi.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 1, 'initial': 1000, 'offset': 0}；只输出'PVI_1'；原目录：pvi（length=1）；追踪：PF01319；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_pvi_pvi_1_1d', 'root_function': 'f_c573558e21_pvi', 'required_inputs': ['close', 'volume'], 'parameters': {'length': 1, 'initial': 1000, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'PVI_1', 'gate_bars': 1, 'kernel': 'kernel_41400ad1c252f1b6', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_pvi_pvi_1_1d', {})
class Factor_ptac_pvi_pvi_1_1d(PublicFactor):
    name = 'ptac_pvi_pvi_1_1d'
    description = "PVI_t=PVI_{t−1}×(1+R_t)若V_t>V_{t−1}，否则保持；初值按来源；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/volume/pvi.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 1, 'initial': 1000, 'offset': 0}；只输出'PVI_1'；原目录：pvi（length=1）；追踪：PF01319；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
