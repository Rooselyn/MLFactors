"""PyTI

公式：完整数值定义为附录独立函数pyti_directional_indicators_negative_directional_index；固定参数={'period': 14}；原目录定义：源码算子/递推链：ndi = 100 * smma(negative_directional_movement(high_data, low_data), period) / atr(close_data, high_data, low_data, period)；输出=ndi；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/directional_indicators.py#L90)；原目录：directional_indicators.negative_directional_index（period等由调用方指定）；追踪：PF01421；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'pyti_negative_directional_index_14d', 'root_function': 'pyti_directional_indicators_negative_directional_index', 'required_inputs': ['close_data', 'high_data', 'low_data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'negative_directional_index', 'kernel': 'kernel_edd580b7613ea334', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_negative_directional_index_14d', {})
class Factor_pyti_negative_directional_index_14d(PublicFactor):
    name = 'pyti_negative_directional_index_14d'
    description = "完整数值定义为附录独立函数pyti_directional_indicators_negative_directional_index；固定参数={'period': 14}；原目录定义：源码算子/递推链：ndi = 100 * smma(negative_directional_movement(high_data, low_data), period) / atr(close_data, high_data, low_data, period)；输出=ndi；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/directional_indicators.py#L90)；原目录：directional_indicators.negative_directional_index（period等由调用方指定）；追踪：PF01421；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
