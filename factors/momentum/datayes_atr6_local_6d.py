"""通联 DataYes／优矿424因子库

公式：TR=max(H−L,abs(H−C[-1]),abs(L−C[-1]))，第一根TR=H−L；首N根TR算术均值种子，随后(N−1)/N递推；除当日adj_factor。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：ATR6；追踪：DY0246；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'datayes_atr6_local_6d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'atr', 'n': 6, 'output': 0}, 'supplied_parameters': {'kind': 'atr', 'n': 6, 'output': 0}, 'output_index': 0, 'output_label': 'ATR6', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_atr6_local_6d', {})
class Factor_datayes_atr6_local_6d(PublicFactor):
    name = 'datayes_atr6_local_6d'
    description = 'TR=max(H−L,abs(H−C[-1]),abs(L−C[-1]))，第一根TR=H−L；首N根TR算术均值种子，随后(N−1)/N递推；除当日adj_factor。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：ATR6；追踪：DY0246；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
