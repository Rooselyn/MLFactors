"""PyTI

公式：完整数值定义为附录独立函数pyti_directional_indicators_calculate_up_moves；固定参数={}；原目录定义：源码算子/递推链：up_moves = [high_data[idx] - high_data[idx - 1] for idx in range(1, len(high_data))]；输出=[nan] + up_moves；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/directional_indicators.py#L11)；原目录：directional_indicators.calculate_up_moves（period等由调用方指定）；追踪：PF01416；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
}
SPEC = {'name': 'pyti_calculate_up_moves_2d', 'root_function': 'pyti_directional_indicators_calculate_up_moves', 'required_inputs': ['high_data'], 'parameters': {}, 'supplied_parameters': {}, 'output_index': 0, 'output_label': 'calculate_up_moves', 'kernel': 'kernel_20799f01f3034ae4', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_calculate_up_moves_2d', {})
class Factor_pyti_calculate_up_moves_2d(PublicFactor):
    name = 'pyti_calculate_up_moves_2d'
    description = '完整数值定义为附录独立函数pyti_directional_indicators_calculate_up_moves；固定参数={}；原目录定义：源码算子/递推链：up_moves = [high_data[idx] - high_data[idx - 1] for idx in range(1, len(high_data))]；输出=[nan] + up_moves；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/directional_indicators.py#L11)；原目录：directional_indicators.calculate_up_moves（period等由调用方指定）；追踪：PF01416；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
