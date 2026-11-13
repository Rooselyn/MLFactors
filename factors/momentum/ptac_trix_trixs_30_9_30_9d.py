"""Pandas TA Classic

公式：100×(EMA³(C,n)/delay(EMA³(C,n),1)−1)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/trix.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'signal': 9, 'scalar': 100, 'talib': False, 'drift': 1, 'offset': 0}；只输出'TRIXs_30_9'；原目录：trix（length=30, signal=9, scalar=100）；追踪：PF01216；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_trix_trixs_30_9_30_9d', 'root_function': 'f_75a1a4352d_trix', 'required_inputs': ['close'], 'parameters': {'length': 30, 'signal': 9, 'scalar': 100, 'talib': False, 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'TRIXs_30_9', 'gate_bars': 1, 'kernel': 'kernel_8685875ff6d035d7', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_trix_trixs_30_9_30_9d', {})
class Factor_ptac_trix_trixs_30_9_30_9d(PublicFactor):
    name = 'ptac_trix_trixs_30_9_30_9d'
    description = "100×(EMA³(C,n)/delay(EMA³(C,n),1)−1)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/trix.py#L18)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 30, 'signal': 9, 'scalar': 100, 'talib': False, 'drift': 1, 'offset': 0}；只输出'TRIXs_30_9'；原目录：trix（length=30, signal=9, scalar=100）；追踪：PF01216；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
