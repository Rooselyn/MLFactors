"""FinTA

公式：固定公开源码默认参数：{'period': 10, 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：FISH(cls, ohlc: DataFrame, period: int=10, adjust: bool=True): from numpy import log, seterr<br>seterr(divide='ignore')<br>med = (ohlc['high'] + ohlc['low']) / 2<br>ndaylow = med.rolling(window=period).min()<br>ndayhigh = med.rolling(window=period).max()<br>raw = 2 * ((med - ndaylow) / (ndayhigh - ndaylow)) - 1<br>smooth = raw.ewm(span=5, adjust=adjust).mean()<br>_smooth = smooth.fillna(0)<br>return pd.Series(log((1 + _smooth) / (1 - _smooth)).ewm(span=3, adjust=adjust).mean(), name='{0} period FISH.'.format(period))；原目录：FISH（period=10）；追踪：PF01024；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_fish_10d', 'engine': 'finta', 'root_function': 'TA.FISH', 'parameters': {'period': 10, 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_fish_10d', {})
class Factor_finta_fish_10d(PublicFactor):
    name = 'finta_fish_10d'
    description = "固定公开源码默认参数：{'period': 10, 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：FISH(cls, ohlc: DataFrame, period: int=10, adjust: bool=True): from numpy import log, seterr<br>seterr(divide='ignore')<br>med = (ohlc['high'] + ohlc['low']) / 2<br>ndaylow = med.rolling(window=period).min()<br>ndayhigh = med.rolling(window=period).max()<br>raw = 2 * ((med - ndaylow) / (ndayhigh - ndaylow)) - 1<br>smooth = raw.ewm(span=5, adjust=adjust).mean()<br>_smooth = smooth.fillna(0)<br>return pd.Series(log((1 + _smooth) / (1 - _smooth)).ewm(span=3, adjust=adjust).mean(), name='{0} period FISH.'.format(period))；原目录：FISH（period=10）；追踪：PF01024；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
