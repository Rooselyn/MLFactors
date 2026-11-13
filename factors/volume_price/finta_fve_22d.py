"""FinTA

公式：固定公开源码默认参数：{'period': 22, 'factor': 0.3}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：FVE(cls, ohlc: DataFrame, period: int=22, factor: int=0.3): hl2 = (ohlc['high'] + ohlc['low']) / 2<br>tp = TA.TP(ohlc)<br>smav = ohlc['volume'].rolling(window=period).mean()<br>mf = pd.Series(ohlc['close'] - hl2 + tp.diff(), name='mf')<br>_mf = pd.concat([ohlc['close'], ohlc['volume'], mf], axis=1)<br>def vol_shift(row):<br>    if row['mf'] > factor * row['close'] / 100:<br>        return row['volume']<br>    elif row['mf'] < -factor * row['close'] / 100:<br>        return -row['volume']<br>    else:<br>        return 0<br>_mf['vol_shift'] = _mf.apply(vol_shift, axis=1)<br>_sum = _mf['vol_shift'].rolling(window=period).sum()<br>return pd.Series(_sum / smav / period * 100)；TP(cls, ohlc: DataFrame): return pd.Series((ohlc['high'] + ohlc['low'] + ohlc['close']) / 3, name='TP')；原目录：FVE（period=22, factor=0.3）；追踪：PF01029；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_fve_22d', 'engine': 'finta', 'root_function': 'TA.FVE', 'parameters': {'period': 22, 'factor': 0.3}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_fve_22d', {})
class Factor_finta_fve_22d(PublicFactor):
    name = 'finta_fve_22d'
    description = "固定公开源码默认参数：{'period': 22, 'factor': 0.3}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：FVE(cls, ohlc: DataFrame, period: int=22, factor: int=0.3): hl2 = (ohlc['high'] + ohlc['low']) / 2<br>tp = TA.TP(ohlc)<br>smav = ohlc['volume'].rolling(window=period).mean()<br>mf = pd.Series(ohlc['close'] - hl2 + tp.diff(), name='mf')<br>_mf = pd.concat([ohlc['close'], ohlc['volume'], mf], axis=1)<br>def vol_shift(row):<br>    if row['mf'] > factor * row['close'] / 100:<br>        return row['volume']<br>    elif row['mf'] < -factor * row['close'] / 100:<br>        return -row['volume']<br>    else:<br>        return 0<br>_mf['vol_shift'] = _mf.apply(vol_shift, axis=1)<br>_sum = _mf['vol_shift'].rolling(window=period).sum()<br>return pd.Series(_sum / smav / period * 100)；TP(cls, ohlc: DataFrame): return pd.Series((ohlc['high'] + ohlc['low'] + ohlc['close']) / 3, name='TP')；原目录：FVE（period=22, factor=0.3）；追踪：PF01029；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
