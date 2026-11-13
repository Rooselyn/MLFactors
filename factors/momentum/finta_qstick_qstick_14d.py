"""FinTA

公式：mean(C−O,n)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1773)。；固定默认参数={'period': 14}；实际单列输出='QSTICK'；修正仅返回末14根实体/14的错误；恢复为全日期滚动14日实体均值。；原目录：QSTICK（period=14）；追踪：PF01022；[来源](https://github.com/peerchemist/finta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'finta_qstick_qstick_14d', 'root_function': 'TA.QSTICK', 'parameters': {'period': 14}, 'output_index': 0, 'output_label': 'QSTICK', 'kernel': 'kernel_85a7bc3914dbe049', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_qstick_qstick_14d', {})
class Factor_finta_qstick_qstick_14d(PublicFactor):
    name = 'finta_qstick_qstick_14d'
    description = "mean(C−O,n)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1773)。；固定默认参数={'period': 14}；实际单列输出='QSTICK'；修正仅返回末14根实体/14的错误；恢复为全日期滚动14日实体均值。；原目录：QSTICK（period=14）；追踪：PF01022；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
