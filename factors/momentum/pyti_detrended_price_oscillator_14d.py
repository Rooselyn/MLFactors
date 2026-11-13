"""PyTI

公式：完整数值定义为附录独立函数pyti_detrended_price_oscillator_detrended_price_oscillator；固定参数={'period': 14}；原目录定义：源码算子/递推链：shift = period // 2 + 1；dop = [data[idx] - mean(data[idx + 1 - shift - period:idx + 1 - shift]) for idx in range(period + shift - 1, len(data))]；输出=dop；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/detrended_price_oscillator.py#L6)；原目录：detrended_price_oscillator.detrended_price_oscillator（period等由调用方指定）；追踪：PF01415；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_detrended_price_oscillator_14d', 'root_function': 'pyti_detrended_price_oscillator_detrended_price_oscillator', 'required_inputs': ['data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'detrended_price_oscillator', 'kernel': 'kernel_53b312a836008ca9', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_detrended_price_oscillator_14d', {})
class Factor_pyti_detrended_price_oscillator_14d(PublicFactor):
    name = 'pyti_detrended_price_oscillator_14d'
    description = "完整数值定义为附录独立函数pyti_detrended_price_oscillator_detrended_price_oscillator；固定参数={'period': 14}；原目录定义：源码算子/递推链：shift = period // 2 + 1；dop = [data[idx] - mean(data[idx + 1 - shift - period:idx + 1 - shift]) for idx in range(period + shift - 1, len(data))]；输出=dop；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/detrended_price_oscillator.py#L6)；原目录：detrended_price_oscillator.detrended_price_oscillator（period等由调用方指定）；追踪：PF01415；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
