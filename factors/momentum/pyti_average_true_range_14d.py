"""PyTI

公式：完整数值定义为附录独立函数pyti_average_true_range_average_true_range；固定参数={'period': 14}；原目录定义：ATR_t=(ATR_{t−1}(n−1)+TR_t)/n；首值为n期TR均值；初始化/平滑变体按来源；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/average_true_range.py#L5)；原目录：average_true_range.average_true_range（period等由调用方指定）；追踪：PF01403；[来源](https://github.com/kylejusticemagnuson/pyti)。
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
SPEC = {'name': 'pyti_average_true_range_14d', 'root_function': 'pyti_average_true_range_average_true_range', 'required_inputs': ['close_data', 'high_data', 'low_data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'average_true_range', 'kernel': 'kernel_2a1855f9e54c41e6', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_average_true_range_14d', {})
class Factor_pyti_average_true_range_14d(PublicFactor):
    name = 'pyti_average_true_range_14d'
    description = "完整数值定义为附录独立函数pyti_average_true_range_average_true_range；固定参数={'period': 14}；原目录定义：ATR_t=(ATR_{t−1}(n−1)+TR_t)/n；首值为n期TR均值；初始化/平滑变体按来源；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/average_true_range.py#L5)；原目录：average_true_range.average_true_range（period等由调用方指定）；追踪：PF01403；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
