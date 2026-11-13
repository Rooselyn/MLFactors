"""FinTA

公式：固定公开源码默认参数：{'period_fast': 12, 'period_slow': 30, 'k_period': 10, 'd_period': 3, 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：EVSTC(cls, ohlc: DataFrame, period_fast: int=12, period_slow: int=30, k_period: int=10, d_period: int=3, adjust: bool=True): ema_slow = cls.EVWMA(ohlc, period_slow)<br>ema_fast = cls.EVWMA(ohlc, period_fast)<br>macd = ema_fast - ema_slow<br>STOK = pd.Series((macd - macd.rolling(window=k_period).min()) / (macd.rolling(window=k_period).max() - macd.rolling(window=k_period).min()) * 100)<br>STOD = STOK.rolling(window=d_period).mean()<br>STOD_DoubleSmooth = STOD.rolling(window=d_period).mean()<br>return pd.Series(STOD_DoubleSmooth, name='{0} period EVSTC'.format(k_period))；EVWMA(cls, ohlcv: DataFrame, period: int=20): vol_sum = ohlcv['volume'].rolling(window=period).sum()<br>x = (vol_sum - ohlcv['volume']) / vol_sum<br>y = ohlcv['volume'] * ohlcv['close'] / vol_sum<br>evwma = [0]<br>for x, y in zip(x.fillna(0).iteritems(), y.iteritems()):<br>    if x[1] == 0 or y[1] == 0:<br>        evwma.append(0)<br>    else:<br>        evwma.append(evwma[-1] * x[1] + y[1])<br>return pd.Series(evwma[1:], index=ohlcv.index, name='{0} period EVWMA.'.format(period))；原目录：EVSTC（period_fast=12, period_slow=30, k_period=10, d_period=3）；追踪：PF01033；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_evstc_12_30_10_3d', 'engine': 'finta', 'root_function': 'TA.EVSTC', 'parameters': {'period_fast': 12, 'period_slow': 30, 'k_period': 10, 'd_period': 3, 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_evstc_12_30_10_3d', {})
class Factor_finta_evstc_12_30_10_3d(PublicFactor):
    name = 'finta_evstc_12_30_10_3d'
    description = "固定公开源码默认参数：{'period_fast': 12, 'period_slow': 30, 'k_period': 10, 'd_period': 3, 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：EVSTC(cls, ohlc: DataFrame, period_fast: int=12, period_slow: int=30, k_period: int=10, d_period: int=3, adjust: bool=True): ema_slow = cls.EVWMA(ohlc, period_slow)<br>ema_fast = cls.EVWMA(ohlc, period_fast)<br>macd = ema_fast - ema_slow<br>STOK = pd.Series((macd - macd.rolling(window=k_period).min()) / (macd.rolling(window=k_period).max() - macd.rolling(window=k_period).min()) * 100)<br>STOD = STOK.rolling(window=d_period).mean()<br>STOD_DoubleSmooth = STOD.rolling(window=d_period).mean()<br>return pd.Series(STOD_DoubleSmooth, name='{0} period EVSTC'.format(k_period))；EVWMA(cls, ohlcv: DataFrame, period: int=20): vol_sum = ohlcv['volume'].rolling(window=period).sum()<br>x = (vol_sum - ohlcv['volume']) / vol_sum<br>y = ohlcv['volume'] * ohlcv['close'] / vol_sum<br>evwma = [0]<br>for x, y in zip(x.fillna(0).iteritems(), y.iteritems()):<br>    if x[1] == 0 or y[1] == 0:<br>        evwma.append(0)<br>    else:<br>        evwma.append(evwma[-1] * x[1] + y[1])<br>return pd.Series(evwma[1:], index=ohlcv.index, name='{0} period EVWMA.'.format(period))；原目录：EVSTC（period_fast=12, period_slow=30, k_period=10, d_period=3）；追踪：PF01033；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
