"""Pandas TA Classic

公式：E_t=C_t/n+(1−1/n)E_{t−1}；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/rma.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'offset': 0}；只输出'RMA_10'；原目录：rma（length=10, alpha=0.5）；追踪：PF01241；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_rma_rma_10_10d', 'root_function': 'f_f792ccf1ec_rma', 'required_inputs': ['close'], 'parameters': {'length': 10, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'RMA_10', 'gate_bars': 1, 'kernel': 'kernel_8d66e45a60279686', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_rma_rma_10_10d', {})
class Factor_ptac_rma_rma_10_10d(PublicFactor):
    name = 'ptac_rma_rma_10_10d'
    description = "E_t=C_t/n+(1−1/n)E_{t−1}；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/overlap/rma.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 10, 'offset': 0}；只输出'RMA_10'；原目录：rma（length=10, alpha=0.5）；追踪：PF01241；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
