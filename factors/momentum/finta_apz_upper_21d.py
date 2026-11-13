"""FinTA

公式：源码算子/递推链：price_range = Series((ohlc['high'] - ohlc['low']).ewm(span=period, adjust=adjust).mean())；volatility_value = Series(price_range.ewm(span=period, adjust=adjust).mean(), name='vol_val')；upper_band = Series(volatility_value * dev_factor + MA, name='UPPER')；lower_band = Series(MA - volatility_value * dev_factor, name='LOWER')；输出=concat([upper_band, lower_band], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1910)。；固定默认参数={'period': 21, 'dev_factor': 2, 'MA': None, 'adjust': True}；实际单列输出='UPPER'；；原目录：APZ（period=21, dev_factor=2, MA=None）；追踪：PF01026；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_apz_upper_21d', 'root_function': 'TA.APZ', 'parameters': {'period': 21, 'dev_factor': 2, 'MA': None, 'adjust': True}, 'output_index': 0, 'output_label': 'UPPER', 'kernel': 'kernel_668011808ee4bd4b', 'engine': 'finta', 'minimum': 1, 'gate_bars': 1}

@register_factor
@fixed_factor('finta_apz_upper_21d', {})
class Factor_finta_apz_upper_21d(PublicFactor):
    name = 'finta_apz_upper_21d'
    description = "源码算子/递推链：price_range = Series((ohlc['high'] - ohlc['low']).ewm(span=period, adjust=adjust).mean())；volatility_value = Series(price_range.ewm(span=period, adjust=adjust).mean(), name='vol_val')；upper_band = Series(volatility_value * dev_factor + MA, name='UPPER')；lower_band = Series(MA - volatility_value * dev_factor, name='LOWER')；输出=concat([upper_band, lower_band], axis=1)；确切输出列/初始化见[源码](https://github.com/peerchemist/finta/blob/af01fa594995de78f5ada5c336e61cd87c46b151/finta/finta.py#L1910)。；固定默认参数={'period': 21, 'dev_factor': 2, 'MA': None, 'adjust': True}；实际单列输出='UPPER'；；原目录：APZ（period=21, dev_factor=2, MA=None）；追踪：PF01026；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
