"""FinTA

公式：DIF=EVWMA(C,V,fast)−EVWMA(C,V,slow)，Signal=EMA(DIF,signal)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L617)。；固定默认参数={'period_fast': 20, 'period_slow': 40, 'signal': 9, 'adjust': True}；实际单列输出='MACD'；；原目录：EV_MACD（period_fast=20, period_slow=40, signal=9）；追踪：PF00982；[来源](https://github.com/peerchemist/finta)。
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
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'finta_ev_macd_macd_20_40_9d', 'root_function': 'TA.EV_MACD', 'parameters': {'period_fast': 20, 'period_slow': 40, 'signal': 9, 'adjust': True}, 'output_index': 0, 'output_label': 'MACD', 'kernel': 'kernel_88a7fe4bc1b27067', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_ev_macd_macd_20_40_9d', {})
class Factor_finta_ev_macd_macd_20_40_9d(PublicFactor):
    name = 'finta_ev_macd_macd_20_40_9d'
    description = "DIF=EVWMA(C,V,fast)−EVWMA(C,V,slow)，Signal=EMA(DIF,signal)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L617)。；固定默认参数={'period_fast': 20, 'period_slow': 40, 'signal': 9, 'adjust': True}；实际单列输出='MACD'；；原目录：EV_MACD（period_fast=20, period_slow=40, signal=9）；追踪：PF00982；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
