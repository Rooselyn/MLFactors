"""Pandas TA Classic

公式：100×(EMA(V,fast)−EMA(V,slow))/EMA(V,slow)；Signal=EMA(PVO,signal)；Hist=PVO−Signal；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/pvo.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'signal': 9, 'scalar': 100, 'offset': 0}；只输出'PVOs_12_26_9'；原目录：pvo（fast=12, slow=26, signal=9, scalar=100）；追踪：PF01201；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ptac_pvo_pvos_12_26_9_12_26_9d', 'root_function': 'f_347797dcdf_pvo', 'required_inputs': ['volume'], 'parameters': {'fast': 12, 'slow': 26, 'signal': 9, 'scalar': 100, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 2, 'output_label': 'PVOs_12_26_9', 'gate_bars': 1, 'kernel': 'kernel_5bffca64abddc8c4', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_pvo_pvos_12_26_9_12_26_9d', {})
class Factor_ptac_pvo_pvos_12_26_9_12_26_9d(PublicFactor):
    name = 'ptac_pvo_pvos_12_26_9_12_26_9d'
    description = "100×(EMA(V,fast)−EMA(V,slow))/EMA(V,slow)；Signal=EMA(PVO,signal)；Hist=PVO−Signal；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/pvo.py#L12)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 12, 'slow': 26, 'signal': 9, 'scalar': 100, 'offset': 0}；只输出'PVOs_12_26_9'；原目录：pvo（fast=12, slow=26, signal=9, scalar=100）；追踪：PF01201；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
