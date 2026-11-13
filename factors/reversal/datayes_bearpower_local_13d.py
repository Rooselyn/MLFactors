"""通联 DataYes／优矿424因子库

公式：Bull=H−EMA13(C)，Bear=L−EMA13(C)，EMA首值种子adjust=False；均除当日adj_factor。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：BearPower；追踪：DY0204；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'datayes_bearpower_local_13d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'bullbear', 'n': 13, 'output': 1}, 'supplied_parameters': {'kind': 'bullbear', 'n': 13, 'output': 1}, 'output_index': 0, 'output_label': 'BearPower', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_bearpower_local_13d', {})
class Factor_datayes_bearpower_local_13d(PublicFactor):
    name = 'datayes_bearpower_local_13d'
    description = 'Bull=H−EMA13(C)，Bear=L−EMA13(C)，EMA首值种子adjust=False；均除当日adj_factor。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：BearPower；追踪：DY0204；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
