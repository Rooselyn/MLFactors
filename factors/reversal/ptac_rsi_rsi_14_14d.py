"""Pandas TA Classic

公式：U=RMA(max(ΔC,0),n)，D=RMA(max(−ΔC,0),n)；100−100/(1+U/D)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/rsi.py#L14)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'scalar': 100, 'talib': False, 'drift': 1, 'offset': 0}；只输出'RSI_14'；原目录：rsi（length=14, scalar=100）；追踪：PF01203；[来源](https://github.com/xgboosted/pandas-ta-classic)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ptac_rsi_rsi_14_14d', 'root_function': 'f_20aabf2300_rsi', 'required_inputs': ['close'], 'parameters': {'length': 14, 'scalar': 100, 'talib': False, 'drift': 1, 'offset': 0}, 'supplied_parameters': {'talib': False, 'lookahead': False, 'offset': 0}, 'output_index': 0, 'output_label': 'RSI_14', 'gate_bars': 1, 'kernel': 'kernel_f6960b2e50104da1', 'engine': 'ptac', 'minimum': 1}

@register_factor
@fixed_factor('ptac_rsi_rsi_14_14d', {})
class Factor_ptac_rsi_rsi_14_14d(PublicFactor):
    name = 'ptac_rsi_rsi_14_14d'
    description = "U=RMA(max(ΔC,0),n)，D=RMA(max(−ΔC,0),n)；100−100/(1+U/D)；[完整算法/输出列](https://github.com/xgboosted/pandas-ta-classic/blob/74e91a71b56e12ef17a47de42e601d19573ee0fb/pandas_ta_classic/momentum/rsi.py#L14)；完整独立Python定义见本行实现方法指定的数值核；有效参数={'length': 14, 'scalar': 100, 'talib': False, 'drift': 1, 'offset': 0}；只输出'RSI_14'；原目录：rsi（length=14, scalar=100）；追踪：PF01203；[来源](https://github.com/xgboosted/pandas-ta-classic)。"
    INPUTS = INPUTS
    SPEC = SPEC
