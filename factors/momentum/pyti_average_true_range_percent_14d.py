"""PyTI

公式：完整数值定义为附录独立函数pyti_average_true_range_percent_average_true_range_percent；固定参数={'period': 14}；原目录定义：100×ATR(n)/C；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/average_true_range_percent.py#L8)；原目录：average_true_range_percent.average_true_range_percent（period等由调用方指定）；追踪：PF01404；[来源](https://github.com/kylejusticemagnuson/pyti)。
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
SPEC = {'name': 'pyti_average_true_range_percent_14d', 'root_function': 'pyti_average_true_range_percent_average_true_range_percent', 'required_inputs': ['close_data', 'high_data', 'low_data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'average_true_range_percent', 'kernel': 'kernel_d1cc6531a6a4850a', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_average_true_range_percent_14d', {})
class Factor_pyti_average_true_range_percent_14d(PublicFactor):
    name = 'pyti_average_true_range_percent_14d'
    description = "完整数值定义为附录独立函数pyti_average_true_range_percent_average_true_range_percent；固定参数={'period': 14}；原目录定义：100×ATR(n)/C；[确切算法](https://github.com/kylejusticemagnuson/pyti/blob/dd3e8a8cac846f0ecf28ff2a6454265bb40f1573/pyti/average_true_range_percent.py#L8)；原目录：average_true_range_percent.average_true_range_percent（period等由调用方指定）；追踪：PF01404；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
