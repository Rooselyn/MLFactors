"""PyTI

公式：完整数值定义为附录独立函数pyti_volatility_volatility；固定参数={'period': 20}；原目录定义：源码算子/递推链：volatility = sd(data, period) / sv(data, period)；输出=volatility；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/volatility.py#L5)；原目录：volatility.volatility（period等由调用方指定）；追踪：PF01462；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_volatility_20d', 'root_function': 'pyti_volatility_volatility', 'required_inputs': ['data'], 'parameters': {'period': 20}, 'supplied_parameters': {'period': 20}, 'output_index': 0, 'output_label': 'volatility', 'kernel': 'kernel_3e08c7fc44278419', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_volatility_20d', {})
class Factor_pyti_volatility_20d(PublicFactor):
    name = 'pyti_volatility_20d'
    description = "完整数值定义为附录独立函数pyti_volatility_volatility；固定参数={'period': 20}；原目录定义：源码算子/递推链：volatility = sd(data, period) / sv(data, period)；输出=volatility；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/volatility.py#L5)；原目录：volatility.volatility（period等由调用方指定）；追踪：PF01462；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
