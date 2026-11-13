"""PyTI

公式：完整数值定义为附录独立函数pyti_chande_momentum_oscillator_chande_momentum_oscillator；固定参数={'period': 14}；原目录定义：100×(sum(max(ΔC,0),n)−sum(max(−ΔC,0),n))/sum(abs(ΔC),n)；是否Wilder平滑按来源；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/chande_momentum_oscillator.py#L6)；原目录：chande_momentum_oscillator.chande_momentum_oscillator（period等由调用方指定）；追踪：PF01413；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_chande_momentum_oscillator_14d', 'root_function': 'pyti_chande_momentum_oscillator_chande_momentum_oscillator', 'required_inputs': ['close_data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'chande_momentum_oscillator', 'kernel': 'kernel_6ea7f5e03b8a82e3', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_chande_momentum_oscillator_14d', {})
class Factor_pyti_chande_momentum_oscillator_14d(PublicFactor):
    name = 'pyti_chande_momentum_oscillator_14d'
    description = "完整数值定义为附录独立函数pyti_chande_momentum_oscillator_chande_momentum_oscillator；固定参数={'period': 14}；原目录定义：100×(sum(max(ΔC,0),n)−sum(max(−ΔC,0),n))/sum(abs(ΔC),n)；是否Wilder平滑按来源；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/chande_momentum_oscillator.py#L6)；原目录：chande_momentum_oscillator.chande_momentum_oscillator（period等由调用方指定）；追踪：PF01413；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
