"""PyTI

公式：完整数值定义为附录独立函数pyti_on_balance_volume_on_balance_volume；固定参数={}；原目录定义：OBV_t=OBV_{t−1}+sign(ΔC_t)×V_t；平盘/初始值按来源；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/on_balance_volume.py#L5)；原目录：on_balance_volume.on_balance_volume（period等由调用方指定）；追踪：PF01442；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'pyti_on_balance_volume_alld', 'root_function': 'pyti_on_balance_volume_on_balance_volume', 'required_inputs': ['close_data', 'volume'], 'parameters': {}, 'supplied_parameters': {}, 'output_index': 0, 'output_label': 'on_balance_volume', 'kernel': 'kernel_0869d8d463c36c3f', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_on_balance_volume_alld', {})
class Factor_pyti_on_balance_volume_alld(PublicFactor):
    name = 'pyti_on_balance_volume_alld'
    description = '完整数值定义为附录独立函数pyti_on_balance_volume_on_balance_volume；固定参数={}；原目录定义：OBV_t=OBV_{t−1}+sign(ΔC_t)×V_t；平盘/初始值按来源；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/on_balance_volume.py#L5)；原目录：on_balance_volume.on_balance_volume（period等由调用方指定）；追踪：PF01442；[来源](https://github.com/kylejusticemagnuson/pyti)。'
    INPUTS = INPUTS
    SPEC = SPEC
