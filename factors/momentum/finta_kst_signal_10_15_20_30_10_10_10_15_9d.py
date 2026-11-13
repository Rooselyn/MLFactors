"""FinTA

公式：Σ_{i=1}^4 i×SMA(ROC(C,roc_i),sma_i)；Signal=SMA(KST,signal)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1345)。；固定默认参数={'r1': 10, 'r2': 15, 'r3': 20, 'r4': 30}；实际单列输出='signal'；；原目录：KST（r1=10, r2=15, r3=20, r4=30）；追踪：PF01005；[来源](https://github.com/peerchemist/finta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'finta_kst_signal_10_15_20_30_10_10_10_15_9d', 'root_function': 'TA.KST', 'parameters': {'r1': 10, 'r2': 15, 'r3': 20, 'r4': 30}, 'output_index': 1, 'output_label': 'signal', 'kernel': 'kernel_7e19b149083d9267', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_kst_signal_10_15_20_30_10_10_10_15_9d', {})
class Factor_finta_kst_signal_10_15_20_30_10_10_10_15_9d(PublicFactor):
    name = 'finta_kst_signal_10_15_20_30_10_10_10_15_9d'
    description = "Σ_{i=1}^4 i×SMA(ROC(C,roc_i),sma_i)；Signal=SMA(KST,signal)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1345)。；固定默认参数={'r1': 10, 'r2': 15, 'r3': 20, 'r4': 30}；实际单列输出='signal'；；原目录：KST（r1=10, r2=15, r3=20, r4=30）；追踪：PF01005；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
