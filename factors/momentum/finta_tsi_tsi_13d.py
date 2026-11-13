"""FinTA

公式：100×EMA(EMA(ΔC,slow),fast)/EMA(EMA(abs(ΔC),slow),fast)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1363)。；固定默认参数={'long': 25, 'short': 13, 'signal': 13, 'column': 'close', 'adjust': True}；实际单列输出='TSI'；；原目录：TSI（long=25, short=13, signal=13）；追踪：PF01006；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_tsi_tsi_13d', 'root_function': 'TA.TSI', 'parameters': {'long': 25, 'short': 13, 'signal': 13, 'column': 'close', 'adjust': True}, 'output_index': 0, 'output_label': 'TSI', 'kernel': 'kernel_fac5755e6a2899c0', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_tsi_tsi_13d', {})
class Factor_finta_tsi_tsi_13d(PublicFactor):
    name = 'finta_tsi_tsi_13d'
    description = "100×EMA(EMA(ΔC,slow),fast)/EMA(EMA(abs(ΔC),slow),fast)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1363)。；固定默认参数={'long': 25, 'short': 13, 'signal': 13, 'column': 'close', 'adjust': True}；实际单列输出='TSI'；；原目录：TSI（long=25, short=13, signal=13）；追踪：PF01006；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
