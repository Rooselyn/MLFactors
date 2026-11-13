"""通联 DataYes／优矿424因子库

公式：VDIFF=EMA12(V)−EMA26(V)；VDEA=EMA9(VDIFF)；VMACD=2×(VDIFF−VDEA)；EMA首值种子adjust=False，单位股。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：VDEA；追踪：DY0016；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'datayes_vdea_local_12_26_9d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'vmacd', 'n': 0, 'output': 1}, 'supplied_parameters': {'kind': 'vmacd', 'n': 0, 'output': 1}, 'output_index': 0, 'output_label': 'VDEA', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_vdea_local_12_26_9d', {})
class Factor_datayes_vdea_local_12_26_9d(PublicFactor):
    name = 'datayes_vdea_local_12_26_9d'
    description = 'VDIFF=EMA12(V)−EMA26(V)；VDEA=EMA9(VDIFF)；VMACD=2×(VDIFF−VDEA)；EMA首值种子adjust=False，单位股。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：VDEA；追踪：DY0016；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
