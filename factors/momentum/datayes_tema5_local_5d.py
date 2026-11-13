"""通联 DataYes／优矿424因子库

公式：TEMA=3EMA_n(C)−3EMA_n(EMA_n(C))+EMA_n(EMA_n(EMA_n(C)))，EMA首值种子adjust=False；除当日adj_factor。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：TEMA5；追踪：DY0336；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'datayes_tema5_local_5d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'tema', 'n': 5, 'output': 0}, 'supplied_parameters': {'kind': 'tema', 'n': 5, 'output': 0}, 'output_index': 0, 'output_label': 'TEMA5', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_tema5_local_5d', {})
class Factor_datayes_tema5_local_5d(PublicFactor):
    name = 'datayes_tema5_local_5d'
    description = 'TEMA=3EMA_n(C)−3EMA_n(EMA_n(C))+EMA_n(EMA_n(EMA_n(C)))，EMA首值种子adjust=False；除当日adj_factor。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：TEMA5；追踪：DY0336；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
