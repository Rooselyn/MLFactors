"""PyTI

公式：完整数值定义为附录独立函数pyti_directional_indicators_calculate_down_moves；固定参数={}；原目录定义：源码算子/递推链：down_moves = [low_data[idx - 1] - low_data[idx] for idx in range(1, len(low_data))]；输出=[nan] + down_moves；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/directional_indicators.py#L22)；原目录：directional_indicators.calculate_down_moves（period等由调用方指定）；追踪：PF01417；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'pyti_calculate_down_moves_2d', 'root_function': 'pyti_directional_indicators_calculate_down_moves', 'required_inputs': ['low_data'], 'parameters': {}, 'supplied_parameters': {}, 'output_index': 0, 'output_label': 'calculate_down_moves', 'kernel': 'kernel_e1b2c8ad9953fb47', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_calculate_down_moves_2d', {})
class Factor_pyti_calculate_down_moves_2d(PublicFactor):
    name = 'pyti_calculate_down_moves_2d'
    description = '完整数值定义为附录独立函数pyti_directional_indicators_calculate_down_moves；固定参数={}；原目录定义：源码算子/递推链：down_moves = [low_data[idx - 1] - low_data[idx] for idx in range(1, len(low_data))]；输出=[nan] + down_moves；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/directional_indicators.py#L22)；原目录：directional_indicators.calculate_down_moves（period等由调用方指定）；追踪：PF01417；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
