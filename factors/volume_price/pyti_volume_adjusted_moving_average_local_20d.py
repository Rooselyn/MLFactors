"""PyTI

公式：完整数值定义为附录独立函数pyti_volume_adjusted_moving_average_volume_adjusted_moving_average；固定参数={'period': 20}；本地因果修正版：CCI的MAD采用当期N日窗口；VAMA的基准成交量采用当期N日均量，0.67保留；不声称等于原全样本程序。；原目录：volume_adjusted_moving_average.volume_adjusted_moving_average（period等由调用方指定）；追踪：PF01463；[来源](https://github.com/kylejusticemagnuson/pyti)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'pyti_volume_adjusted_moving_average_local_20d', 'root_function': 'pyti_volume_adjusted_moving_average_volume_adjusted_moving_average', 'required_inputs': ['close_data', 'volume'], 'parameters': {'period': 20}, 'supplied_parameters': {'period': 20}, 'output_index': 0, 'output_label': 'volume_adjusted_moving_average', 'kernel': 'kernel_5c3c89fd96aa200f', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_volume_adjusted_moving_average_local_20d', {})
class Factor_pyti_volume_adjusted_moving_average_local_20d(PublicFactor):
    name = 'pyti_volume_adjusted_moving_average_local_20d'
    description = "完整数值定义为附录独立函数pyti_volume_adjusted_moving_average_volume_adjusted_moving_average；固定参数={'period': 20}；本地因果修正版：CCI的MAD采用当期N日窗口；VAMA的基准成交量采用当期N日均量，0.67保留；不声称等于原全样本程序。；原目录：volume_adjusted_moving_average.volume_adjusted_moving_average（period等由调用方指定）；追踪：PF01463；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
