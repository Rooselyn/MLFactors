"""FinTA

公式：源码算子/递推链：vp = ohlcv['volume'] * ohlcv[column]；_fast = Series(vp.ewm(ignore_na=False, span=period_fast, adjust=adjust).mean() / ohlcv['volume'].ewm(ignore_na=False, span=period_fast, adjust=adjust).mean(), name='_fast')；_slow = Series(vp.ewm(ignore_na=False, span=period_slow, adjust=adjust).mean() / ohlcv['volume'].ewm(ignore_na=False, span=period_slow, adjust=adjust).mean(), name='_slow')；MACD = Series(_fast - _slow, name='MACD')；MACD_signal = Series(MACD.ewm(ignore_na=False, span=signal, adjust=adjust).mean(), name='SIGNAL')；输出=concat([MACD, MACD_signal], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L575)。；固定默认参数={'period_fast': 12, 'period_slow': 26, 'signal': 9, 'column': 'close', 'adjust': True}；实际单列输出='MACD'；；原目录：VW_MACD（period_fast=12, period_slow=26, signal=9）；追踪：PF00981；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_vw_macd_macd_12_26_9d', 'root_function': 'TA.VW_MACD', 'parameters': {'period_fast': 12, 'period_slow': 26, 'signal': 9, 'column': 'close', 'adjust': True}, 'output_index': 0, 'output_label': 'MACD', 'kernel': 'kernel_6bfdde4bd7f8dc78', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_vw_macd_macd_12_26_9d', {})
class Factor_finta_vw_macd_macd_12_26_9d(PublicFactor):
    name = 'finta_vw_macd_macd_12_26_9d'
    description = "源码算子/递推链：vp = ohlcv['volume'] * ohlcv[column]；_fast = Series(vp.ewm(ignore_na=False, span=period_fast, adjust=adjust).mean() / ohlcv['volume'].ewm(ignore_na=False, span=period_fast, adjust=adjust).mean(), name='_fast')；_slow = Series(vp.ewm(ignore_na=False, span=period_slow, adjust=adjust).mean() / ohlcv['volume'].ewm(ignore_na=False, span=period_slow, adjust=adjust).mean(), name='_slow')；MACD = Series(_fast - _slow, name='MACD')；MACD_signal = Series(MACD.ewm(ignore_na=False, span=signal, adjust=adjust).mean(), name='SIGNAL')；输出=concat([MACD, MACD_signal], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L575)。；固定默认参数={'period_fast': 12, 'period_slow': 26, 'signal': 9, 'column': 'close', 'adjust': True}；实际单列输出='MACD'；；原目录：VW_MACD（period_fast=12, period_slow=26, signal=9）；追踪：PF00981；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
