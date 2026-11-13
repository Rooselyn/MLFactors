"""通联 DataYes／优矿424因子库

公式：RSV=100×(C−LLV9)/(HHV9−LLV9)；首个有效RSV前K=D=50；K=(2K前值+RSV)/3，D=(2D前值+K)/3，J=3K−2D。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：KDJ_J；追踪：DY0273；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'datayes_kdj_j_local_9_3_3d', 'root_function': 'local_indicator', 'required_inputs': ['x'], 'parameters': {'kind': 'kdj', 'n': 9, 'output': 2}, 'supplied_parameters': {'kind': 'kdj', 'n': 9, 'output': 2}, 'output_index': 0, 'output_label': 'KDJ_J', 'kernel': 'kernel_dac4dd796184c078', 'engine': 'simple', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('datayes_kdj_j_local_9_3_3d', {})
class Factor_datayes_kdj_j_local_9_3_3d(PublicFactor):
    name = 'datayes_kdj_j_local_9_3_3d'
    description = 'RSV=100×(C−LLV9)/(HHV9−LLV9)；首个有效RSV前K=D=50；K=(2K前值+RSV)/3，D=(2D前值+K)/3，J=3K−2D。；明确本地参数口径，不承诺复原通联未公开的边界/初始化。；原目录：KDJ_J；追踪：DY0273；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
