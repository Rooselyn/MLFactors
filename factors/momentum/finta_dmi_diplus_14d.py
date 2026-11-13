"""FinTA

公式：输出+DI与−DI，定义同PLUS_DI/MINUS_DI；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1059)。；固定默认参数={'period': 14, 'adjust': True}；实际单列输出='DI+'；；原目录：DMI（period=14）；追踪：PF00996；[来源](https://github.com/peerchemist/finta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'finta_dmi_diplus_14d', 'root_function': 'TA.DMI', 'parameters': {'period': 14, 'adjust': True}, 'output_index': 0, 'output_label': 'DI+', 'kernel': 'kernel_0d9a26ca22a621b2', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_dmi_diplus_14d', {})
class Factor_finta_dmi_diplus_14d(PublicFactor):
    name = 'finta_dmi_diplus_14d'
    description = "输出+DI与−DI，定义同PLUS_DI/MINUS_DI；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1059)。；固定默认参数={'period': 14, 'adjust': True}；实际单列输出='DI+'；；原目录：DMI（period=14）；追踪：PF00996；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
