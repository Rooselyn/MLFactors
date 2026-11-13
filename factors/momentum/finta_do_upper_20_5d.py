"""FinTA

公式：Upper=max(H,n)，Lower=min(L,n)，Middle=(Upper+Lower)/2；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1042)。；固定默认参数={'upper_period': 20, 'lower_period': 5}；实际单列输出='UPPER'；；原目录：DO（upper_period=20, lower_period=5）；追踪：PF00995；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_do_upper_20_5d', 'root_function': 'TA.DO', 'parameters': {'upper_period': 20, 'lower_period': 5}, 'output_index': 2, 'output_label': 'UPPER', 'kernel': 'kernel_261d55c047a861a3', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_do_upper_20_5d', {})
class Factor_finta_do_upper_20_5d(PublicFactor):
    name = 'finta_do_upper_20_5d'
    description = "Upper=max(H,n)，Lower=min(L,n)，Middle=(Upper+Lower)/2；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1042)。；固定默认参数={'upper_period': 20, 'lower_period': 5}；实际单列输出='UPPER'；；原目录：DO（upper_period=20, lower_period=5）；追踪：PF00995；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
