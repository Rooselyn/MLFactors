"""PyTI

公式：完整数值定义为附录独立函数pyti_commodity_channel_index_commodity_channel_index；固定参数={'period': 14}；本地因果修正版：CCI的MAD采用当期N日窗口；VAMA的基准成交量采用当期N日均量，0.67保留；不声称等于原全样本程序。；原目录：commodity_channel_index.commodity_channel_index（period等由调用方指定）；追踪：PF01414；[来源](https://github.com/kylejusticemagnuson/pyti)。
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
SPEC = {'name': 'pyti_commodity_channel_index_local_14d', 'root_function': 'pyti_commodity_channel_index_commodity_channel_index', 'required_inputs': ['close_data', 'high_data', 'low_data'], 'parameters': {'period': 14}, 'supplied_parameters': {'period': 14}, 'output_index': 0, 'output_label': 'commodity_channel_index', 'kernel': 'kernel_a48df4ec792b0a1d', 'engine': 'pyti', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('pyti_commodity_channel_index_local_14d', {})
class Factor_pyti_commodity_channel_index_local_14d(PublicFactor):
    name = 'pyti_commodity_channel_index_local_14d'
    description = "完整数值定义为附录独立函数pyti_commodity_channel_index_commodity_channel_index；固定参数={'period': 14}；本地因果修正版：CCI的MAD采用当期N日窗口；VAMA的基准成交量采用当期N日均量，0.67保留；不声称等于原全样本程序。；原目录：commodity_channel_index.commodity_channel_index（period等由调用方指定）；追踪：PF01414；[来源](https://github.com/kylejusticemagnuson/pyti)。"
    INPUTS = INPUTS
    SPEC = SPEC
