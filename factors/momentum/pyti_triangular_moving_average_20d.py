"""PyTI

公式：完整数值定义为附录独立函数pyti_triangular_moving_average_triangular_moving_average；固定参数={'period': 20}；原目录定义：两次SMA：奇数n用(n+1)/2与(n+1)/2，偶数n用n/2与n/2+1；具体初始化按来源；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/triangular_moving_average.py#L7)；原目录：triangular_moving_average.triangular_moving_average（period等由调用方指定）；追踪：PF01454；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'pyti_triangular_moving_average_20d', 'root_function': 'pyti_triangular_moving_average_triangular_moving_average', 'required_inputs': ['data'], 'parameters': {'period': 20}, 'supplied_parameters': {'period': 20}, 'output_index': 0, 'output_label': 'triangular_moving_average', 'kernel': 'kernel_78567f93247e4fc9', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_triangular_moving_average_20d', {})
class Factor_pyti_triangular_moving_average_20d(PublicFactor):
    name = 'pyti_triangular_moving_average_20d'
    description = "完整数值定义为附录独立函数pyti_triangular_moving_average_triangular_moving_average；固定参数={'period': 20}；原目录定义：两次SMA：奇数n用(n+1)/2与(n+1)/2，偶数n用n/2与n/2+1；具体初始化按来源；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/triangular_moving_average.py#L7)；原目录：triangular_moving_average.triangular_moving_average（period等由调用方指定）；追踪：PF01454；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
