"""PyTI

公式：完整数值定义为附录独立函数pyti_ultimate_oscillator_buying_pressure；固定参数={}；原目录定义：源码算子/递推链：bp = [close_data[idx] - min(low_data[idx], close_data[idx - 1]) for idx in range(1, len(close_data))]；输出=bp；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/ultimate_oscillator.py#L6)；原目录：ultimate_oscillator.buying_pressure（period等由调用方指定）；追踪：PF01456；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'pyti_buying_pressure_2d', 'root_function': 'pyti_ultimate_oscillator_buying_pressure', 'required_inputs': ['close_data', 'low_data'], 'parameters': {}, 'supplied_parameters': {}, 'output_index': 0, 'output_label': 'buying_pressure', 'kernel': 'kernel_37e693ca79cd8bd8', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_buying_pressure_2d', {})
class Factor_pyti_buying_pressure_2d(PublicFactor):
    name = 'pyti_buying_pressure_2d'
    description = '完整数值定义为附录独立函数pyti_ultimate_oscillator_buying_pressure；固定参数={}；原目录定义：源码算子/递推链：bp = [close_data[idx] - min(low_data[idx], close_data[idx - 1]) for idx in range(1, len(close_data))]；输出=bp；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/ultimate_oscillator.py#L6)；原目录：ultimate_oscillator.buying_pressure（period等由调用方指定）；追踪：PF01456；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
