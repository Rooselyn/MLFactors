"""PyTI

公式：完整数值定义为附录独立函数pyti_hull_moving_average_hull_moving_average；固定参数={'period': 20}；原目录定义：WMA(2WMA(C,n/2)−WMA(C,n),sqrt(n))；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/hull_moving_average.py#L8)；原目录：hull_moving_average.hull_moving_average（period等由调用方指定）；追踪：PF01426；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_hull_moving_average_20d', 'root_function': 'pyti_hull_moving_average_hull_moving_average', 'required_inputs': ['data'], 'parameters': {'period': 20}, 'supplied_parameters': {'period': 20}, 'output_index': 0, 'output_label': 'hull_moving_average', 'kernel': 'kernel_2d2fa7a5ea19a723', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_hull_moving_average_20d', {})
class Factor_pyti_hull_moving_average_20d(PublicFactor):
    name = 'pyti_hull_moving_average_20d'
    description = "完整数值定义为附录独立函数pyti_hull_moving_average_hull_moving_average；固定参数={'period': 20}；原目录定义：WMA(2WMA(C,n/2)−WMA(C,n),sqrt(n))；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/hull_moving_average.py#L8)；原目录：hull_moving_average.hull_moving_average（period等由调用方指定）；追踪：PF01426；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
