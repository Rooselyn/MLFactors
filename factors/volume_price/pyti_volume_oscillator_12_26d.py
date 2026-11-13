"""PyTI

公式：完整数值定义为附录独立函数pyti_volume_oscillator_volume_oscillator；固定参数={'short_period': 12, 'long_period': 26}；原目录定义：源码算子/递推链：vo = 100 * ((sma(volume, short_period) - sma(volume, long_period)) / sma(volume, long_period))；输出=vo；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/volume_oscillator.py#L5)；原目录：volume_oscillator.volume_oscillator（period等由调用方指定）；追踪：PF01466；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'pyti_volume_oscillator_12_26d', 'root_function': 'pyti_volume_oscillator_volume_oscillator', 'required_inputs': ['volume'], 'parameters': {'short_period': 12, 'long_period': 26}, 'supplied_parameters': {'short_period': 12, 'long_period': 26}, 'output_index': 0, 'output_label': 'volume_oscillator', 'kernel': 'kernel_aed8e34536295f4b', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_volume_oscillator_12_26d', {})
class Factor_pyti_volume_oscillator_12_26d(PublicFactor):
    name = 'pyti_volume_oscillator_12_26d'
    description = "完整数值定义为附录独立函数pyti_volume_oscillator_volume_oscillator；固定参数={'short_period': 12, 'long_period': 26}；原目录定义：源码算子/递推链：vo = 100 * ((sma(volume, short_period) - sma(volume, long_period)) / sma(volume, long_period))；输出=vo；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/volume_oscillator.py#L5)；原目录：volume_oscillator.volume_oscillator（period等由调用方指定）；追踪：PF01466；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
