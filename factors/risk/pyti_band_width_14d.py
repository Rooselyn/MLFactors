"""PyTI

公式：完整数值定义为附录独立函数pyti_keltner_bands_band_width；固定参数={'period': 14}；原目录定义：源码算子/递推链：diff = array(high_data) - array(low_data)；输出=bw；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/keltner_bands.py#L9)；原目录：keltner_bands.band_width（period等由调用方指定）；追踪：PF01432；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'pyti_band_width_14d', 'root_function': 'pyti_keltner_bands_band_width', 'required_inputs': ['high_data', 'low_data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'band_width', 'kernel': 'kernel_a0519c78bcb93dba', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_band_width_14d', {})
class Factor_pyti_band_width_14d(PublicFactor):
    name = 'pyti_band_width_14d'
    description = "完整数值定义为附录独立函数pyti_keltner_bands_band_width；固定参数={'period': 14}；原目录定义：源码算子/递推链：diff = array(high_data) - array(low_data)；输出=bw；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/keltner_bands.py#L9)；原目录：keltner_bands.band_width（period等由调用方指定）；追踪：PF01432；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
