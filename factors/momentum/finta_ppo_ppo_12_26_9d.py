"""FinTA

公式：100×(MA(C,fast)−MA(C,slow))/MA(C,slow)；Signal=EMA(PPO,signal)；Hist=PPO−Signal；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L541)。；固定默认参数={'period_fast': 12, 'period_slow': 26, 'signal': 9, 'column': 'close', 'adjust': True}；实际单列输出='PPO'；；原目录：PPO（period_fast=12, period_slow=26, signal=9）；追踪：PF00980；[来源](https://github.com/peerchemist/finta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'finta_ppo_ppo_12_26_9d', 'root_function': 'TA.PPO', 'parameters': {'period_fast': 12, 'period_slow': 26, 'signal': 9, 'column': 'close', 'adjust': True}, 'output_index': 0, 'output_label': 'PPO', 'kernel': 'kernel_2daedd7d871d8033', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_ppo_ppo_12_26_9d', {})
class Factor_finta_ppo_ppo_12_26_9d(PublicFactor):
    name = 'finta_ppo_ppo_12_26_9d'
    description = "100×(MA(C,fast)−MA(C,slow))/MA(C,slow)；Signal=EMA(PPO,signal)；Hist=PPO−Signal；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L541)。；固定默认参数={'period_fast': 12, 'period_slow': 26, 'signal': 9, 'column': 'close', 'adjust': True}；实际单列输出='PPO'；；原目录：PPO（period_fast=12, period_slow=26, signal=9）；追踪：PF00980；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
