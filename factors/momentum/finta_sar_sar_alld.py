"""FinTA

公式：SAR_t=SAR_{t−1}+AF×(EP−SAR_{t−1})；新极值提高AF，穿越前轨反转并重置EP/AF；上下界限制按源码；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L821)。；固定默认参数={'af': 0.02, 'amax': 0.2}；实际单列输出='SAR'；修正全样本振幅标准差种子：种子仅用首根已知K线，SAR0=2L0−H0；其余分支按附录。；原目录：SAR（af=0.02, amax=0.2）；追踪：PF00988；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_sar_sar_alld', 'root_function': 'TA.SAR', 'parameters': {'af': 0.02, 'amax': 0.2}, 'output_index': 0, 'output_label': 'SAR', 'kernel': 'kernel_1c70de4b8f8223da', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_sar_sar_alld', {})
class Factor_finta_sar_sar_alld(PublicFactor):
    name = 'finta_sar_sar_alld'
    description = "SAR_t=SAR_{t−1}+AF×(EP−SAR_{t−1})；新极值提高AF，穿越前轨反转并重置EP/AF；上下界限制按源码；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L821)。；固定默认参数={'af': 0.02, 'amax': 0.2}；实际单列输出='SAR'；修正全样本振幅标准差种子：种子仅用首根已知K线，SAR0=2L0−H0；其余分支按附录。；原目录：SAR（af=0.02, amax=0.2）；追踪：PF00988；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
