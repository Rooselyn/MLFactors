"""通联 DataYes／优矿424因子库

公式：EMA_n(V)，V=vol×100股；首值种子，alpha=2/(n+1)，adjust=False。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：VEMA12；追踪：DY0019；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'datayes_vema12_local_12d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'vema', 'n': 12, 'output': 0}, 'supplied_parameters': {'kind': 'vema', 'n': 12, 'output': 0}, 'output_index': 0, 'output_label': 'VEMA12', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_vema12_local_12d', {})
class Factor_datayes_vema12_local_12d(PublicFactor):
    name = 'datayes_vema12_local_12d'
    description = 'EMA_n(V)，V=vol×100股；首值种子，alpha=2/(n+1)，adjust=False。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：VEMA12；追踪：DY0019；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
