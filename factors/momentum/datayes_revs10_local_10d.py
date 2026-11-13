"""通联 DataYes／优矿424因子库

公式：C_t/C_(t−N)，不减1；N为固定交易日滞后。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：REVS10；追踪：DY0280；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'datayes_revs10_local_10d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'price_ratio', 'n': 10, 'output': 0}, 'supplied_parameters': {'kind': 'price_ratio', 'n': 10, 'output': 0}, 'output_index': 0, 'output_label': 'REVS10', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_revs10_local_10d', {})
class Factor_datayes_revs10_local_10d(PublicFactor):
    name = 'datayes_revs10_local_10d'
    description = 'C_t/C_(t−N)，不减1；N为固定交易日滞后。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：REVS10；追踪：DY0280；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
