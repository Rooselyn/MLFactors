"""PyTI

公式：完整数值定义为附录独立函数pyti_price_channels_lower_price_channel；固定参数={'period': 20, 'lower_percent': 5.0}；原目录定义：源码算子/递推链：lower_channel = [val * (1 - float(lower_percent) / 100) for val in emas]；输出=lower_channel；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/price_channels.py#L21)；原目录：price_channels.lower_price_channel（period等由调用方指定）；追踪：PF01444；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_lower_price_channel_20d', 'root_function': 'pyti_price_channels_lower_price_channel', 'required_inputs': ['data'], 'parameters': {'period': 20, 'lower_percent': 5.0}, 'supplied_parameters': {'period': 20, 'lower_percent': 5.0}, 'output_index': 0, 'output_label': 'lower_price_channel', 'kernel': 'kernel_df3e8dc3e936b8cd', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_lower_price_channel_20d', {})
class Factor_pyti_lower_price_channel_20d(PublicFactor):
    name = 'pyti_lower_price_channel_20d'
    description = "完整数值定义为附录独立函数pyti_price_channels_lower_price_channel；固定参数={'period': 20, 'lower_percent': 5.0}；原目录定义：源码算子/递推链：lower_channel = [val * (1 - float(lower_percent) / 100) for val in emas]；输出=lower_channel；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/price_channels.py#L21)；原目录：price_channels.lower_price_channel（period等由调用方指定）；追踪：PF01444；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
