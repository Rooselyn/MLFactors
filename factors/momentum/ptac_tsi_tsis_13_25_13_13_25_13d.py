"""Pandas TA Classic

公式：100×EMA(EMA(ΔC,slow),fast)/EMA(EMA(abs(ΔC),slow),fast)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/tsi.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 13, 'slow': 25, 'signal': 13, 'scalar': 100, 'mamode': 'ema', 'drift': 1, 'offset': 0}；只输出'TSIs_13_25_13'；原目录：tsi（fast=13, slow=25, signal=13, scalar=100, mamode='ema'）；追踪：PF01218；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_tsi_tsis_13_25_13_13_25_13d', 'root_function': 'f_2eab1871df_tsi', 'required_inputs': ['close'], 'parameters': {'fast': 13, 'slow': 25, 'signal': 13, 'scalar': 100, 'mamode': 'ema', 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 1, 'output_label': 'TSIs_13_25_13', 'gate_bars': 1, 'kernel': 'kernel_dbdd809791572224', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_tsi_tsis_13_25_13_13_25_13d', {})
class Factor_ptac_tsi_tsis_13_25_13_13_25_13d(PublicFactor):
    name = 'ptac_tsi_tsis_13_25_13_13_25_13d'
    description = "100×EMA(EMA(ΔC,slow),fast)/EMA(EMA(abs(ΔC),slow),fast)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/tsi.py#L19)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'fast': 13, 'slow': 25, 'signal': 13, 'scalar': 100, 'mamode': 'ema', 'drift': 1, 'offset': 0}；只输出'TSIs_13_25_13'；原目录：tsi（fast=13, slow=25, signal=13, scalar=100, mamode='ema'）；追踪：PF01218；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
