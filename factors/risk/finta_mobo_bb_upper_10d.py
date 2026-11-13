"""FinTA

公式：BBANDS(C,10,0.8)，源码硬编码10和0.8，不直接使用所有传入参数；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L965)。；固定默认参数={'period': 10, 'std_multiplier': 0.8, 'column': 'close'}；实际单列输出='BB_UPPER'；；原目录：MOBO（period=10, std_multiplier=0.8）；追踪：PF00991；[来源](https://github.com/peerchemist/finta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'finta_mobo_bb_upper_10d', 'root_function': 'TA.MOBO', 'parameters': {'period': 10, 'std_multiplier': 0.8, 'column': 'close'}, 'output_index': 0, 'output_label': 'BB_UPPER', 'kernel': 'kernel_528653a9f4d39b05', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_mobo_bb_upper_10d', {})
class Factor_finta_mobo_bb_upper_10d(PublicFactor):
    name = 'finta_mobo_bb_upper_10d'
    description = "BBANDS(C,10,0.8)，源码硬编码10和0.8，不直接使用所有传入参数；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L965)。；固定默认参数={'period': 10, 'std_multiplier': 0.8, 'column': 'close'}；实际单列输出='BB_UPPER'；；原目录：MOBO（period=10, std_multiplier=0.8）；追踪：PF00991；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
