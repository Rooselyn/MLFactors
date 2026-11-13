"""PyTI

公式：完整数值定义为附录独立函数pyti_bollinger_bands_bandwidth；固定参数={'period': 20, 'std': 2.0}；原目录定义：源码算子/递推链：bandwidth = (upper_bollinger_band(data, period, std) - lower_bollinger_band(data, period, std)) / middle_bollinger_band(data, period, std)；输出=bandwidth；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/bollinger_bands.py#L66)；原目录：bollinger_bands.bandwidth（std=2.0）；追踪：PF01408；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_bandwidth_20d', 'root_function': 'pyti_bollinger_bands_bandwidth', 'required_inputs': ['data'], 'parameters': {'period': 20, 'std': 2.0}, 'supplied_parameters': {'period': 20, 'std': 2.0}, 'output_index': 0, 'output_label': 'bandwidth', 'kernel': 'kernel_0731dd0f1b295603', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_bandwidth_20d', {})
class Factor_pyti_bandwidth_20d(PublicFactor):
    name = 'pyti_bandwidth_20d'
    description = "完整数值定义为附录独立函数pyti_bollinger_bands_bandwidth；固定参数={'period': 20, 'std': 2.0}；原目录定义：源码算子/递推链：bandwidth = (upper_bollinger_band(data, period, std) - lower_bollinger_band(data, period, std)) / middle_bollinger_band(data, period, std)；输出=bandwidth；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/bollinger_bands.py#L66)；原目录：bollinger_bands.bandwidth（std=2.0）；追踪：PF01408；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
