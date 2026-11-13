"""PyTI

公式：完整数值定义为附录独立函数pyti_relative_strength_index_relative_strength_index；固定参数={'period': 14}；原目录定义：U=RMA(max(ΔC,0),n)，D=RMA(max(−ΔC,0),n)；100−100/(1+U/D)；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/relative_strength_index.py#L6)；原目录：relative_strength_index.relative_strength_index（period等由调用方指定）；追踪：PF01447；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_relative_strength_index_14d', 'root_function': 'pyti_relative_strength_index_relative_strength_index', 'required_inputs': ['data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'relative_strength_index', 'kernel': 'kernel_58c451e3d1d459a4', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_relative_strength_index_14d', {})
class Factor_pyti_relative_strength_index_14d(PublicFactor):
    name = 'pyti_relative_strength_index_14d'
    description = "完整数值定义为附录独立函数pyti_relative_strength_index_relative_strength_index；固定参数={'period': 14}；原目录定义：U=RMA(max(ΔC,0),n)，D=RMA(max(−ΔC,0),n)；100−100/(1+U/D)；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/relative_strength_index.py#L6)；原目录：relative_strength_index.relative_strength_index（period等由调用方指定）；追踪：PF01447；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
