"""通联 DataYes／优矿424因子库

公式：20日算术均值±2×20日总体标准差(ddof=0)，最后除当日adj_factor；上轨output=0、下轨=1。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：BollDown；追踪：DY0252；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'),
}
SPEC = {'name': 'datayes_bolldown_local_20d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'bbands', 'n': 20, 'output': 1}, 'supplied_parameters': {'kind': 'bbands', 'n': 20, 'output': 1}, 'output_index': 0, 'output_label': 'BollDown', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_bolldown_local_20d', {})
class Factor_datayes_bolldown_local_20d(PublicFactor):
    name = 'datayes_bolldown_local_20d'
    description = '20日算术均值±2×20日总体标准差(ddof=0)，最后除当日adj_factor；上轨output=0、下轨=1。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：BollDown；追踪：DY0252；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
