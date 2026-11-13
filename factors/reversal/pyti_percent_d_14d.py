"""PyTI

公式：完整数值定义为附录独立函数pyti_stochastic_percent_d；固定参数={'period': 14}；原目录定义：源码算子/递推链：输出=percent_d；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/stochastic.py#L25)；原目录：stochastic.percent_d（period等由调用方指定）；追踪：PF01452；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_percent_d_14d', 'root_function': 'pyti_stochastic_percent_d', 'required_inputs': ['data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'percent_d', 'kernel': 'kernel_30a87c712ced31dd', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_percent_d_14d', {})
class Factor_pyti_percent_d_14d(PublicFactor):
    name = 'pyti_percent_d_14d'
    description = "完整数值定义为附录独立函数pyti_stochastic_percent_d；固定参数={'period': 14}；原目录定义：源码算子/递推链：输出=percent_d；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/stochastic.py#L25)；原目录：stochastic.percent_d（period等由调用方指定）；追踪：PF01452；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
