"""FinTA

公式：M=MA(C,n)；Upper=M+k_upσ_n(C)；Lower=M−k_downσ_n(C)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L935)。；固定默认参数={'period': 20, 'MA': None, 'column': 'close', 'std_multiplier': 2}；实际单列输出='BB_LOWER'；；原目录：BBANDS（period=20, MA=None, std_multiplier=2）；追踪：PF00990；[来源](https://github.com/peerchemist/finta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'finta_bbands_bb_lower_20d', 'root_function': 'TA.BBANDS', 'parameters': {'period': 20, 'MA': None, 'column': 'close', 'std_multiplier': 2}, 'output_index': 2, 'output_label': 'BB_LOWER', 'kernel': 'kernel_d9e6181994e1b8e4', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_bbands_bb_lower_20d', {})
class Factor_finta_bbands_bb_lower_20d(PublicFactor):
    name = 'finta_bbands_bb_lower_20d'
    description = "M=MA(C,n)；Upper=M+k_upσ_n(C)；Lower=M−k_downσ_n(C)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L935)。；固定默认参数={'period': 20, 'MA': None, 'column': 'close', 'std_multiplier': 2}；实际单列输出='BB_LOWER'；；原目录：BBANDS（period=20, MA=None, std_multiplier=2）；追踪：PF00990；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
