"""PyTI

公式：完整数值定义为附录独立函数pyti_directional_indicators_positive_directional_movement；固定参数={}；原目录定义：源码算子/递推链：输出=pdm；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/directional_indicators.py#L33)；原目录：directional_indicators.positive_directional_movement（period等由调用方指定）；追踪：PF01418；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'pyti_positive_directional_movement_2d', 'root_function': 'pyti_directional_indicators_positive_directional_movement', 'required_inputs': ['high_data', 'low_data'], 'parameters': {}, 'supplied_parameters': {}, 'output_index': 0, 'output_label': 'positive_directional_movement', 'kernel': 'kernel_b35a7bfaae360e19', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_positive_directional_movement_2d', {})
class Factor_pyti_positive_directional_movement_2d(PublicFactor):
    name = 'pyti_positive_directional_movement_2d'
    description = '完整数值定义为附录独立函数pyti_directional_indicators_positive_directional_movement；固定参数={}；原目录定义：源码算子/递推链：输出=pdm；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/directional_indicators.py#L33)；原目录：directional_indicators.positive_directional_movement（period等由调用方指定）；追踪：PF01418；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
