"""PyTI

公式：完整数值定义为附录独立函数pyti_moving_average_envelope_lower_band；固定参数={'period': 20, 'env_percentage': 0.05}；原目录定义：源码算子/递推链：lb = [val * (1 - float(env_percentage)) for val in cb]；输出=lb；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/moving_average_envelope.py#L27)；原目录：moving_average_envelope.lower_band（period等由调用方指定）；追踪：PF01441；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_lower_band_20d', 'root_function': 'pyti_moving_average_envelope_lower_band', 'required_inputs': ['data'], 'parameters': {'period': 20, 'env_percentage': 0.05}, 'supplied_parameters': {'period': 20, 'env_percentage': 0.05}, 'output_index': 0, 'output_label': 'lower_band', 'kernel': 'kernel_5795e404487465e4', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_lower_band_20d', {})
class Factor_pyti_lower_band_20d(PublicFactor):
    name = 'pyti_lower_band_20d'
    description = "完整数值定义为附录独立函数pyti_moving_average_envelope_lower_band；固定参数={'period': 20, 'env_percentage': 0.05}；原目录定义：源码算子/递推链：lb = [val * (1 - float(env_percentage)) for val in cb]；输出=lb；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/moving_average_envelope.py#L27)；原目录：moving_average_envelope.lower_band（period等由调用方指定）；追踪：PF01441；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
