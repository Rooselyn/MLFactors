"""通联 DataYes／优矿424因子库

公式：100×最近12个有效价格差分中ΔC>0的比例；不把第一根未知差分当作下跌。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：PSY；追踪：DY0211；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'datayes_psy_local_12d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'psychological', 'n': 12, 'output': 0}, 'supplied_parameters': {'kind': 'psychological', 'n': 12, 'output': 0}, 'output_index': 0, 'output_label': 'PSY', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_psy_local_12d', {})
class Factor_datayes_psy_local_12d(PublicFactor):
    name = 'datayes_psy_local_12d'
    description = '100×最近12个有效价格差分中ΔC>0的比例；不把第一根未知差分当作下跌。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：PSY；追踪：DY0211；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
