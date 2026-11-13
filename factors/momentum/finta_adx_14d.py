"""FinTA

公式：固定公开源码默认参数：{'period': 14, 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：ADX(cls, ohlc: DataFrame, period: int=14, adjust: bool=True): dmi = cls.DMI(ohlc, period)<br>return pd.Series(100 * (abs(dmi['DI+'] - dmi['DI-']) / (dmi['DI+'] + dmi['DI-'])).ewm(alpha=1 / period, adjust=adjust).mean(), name='{0} period ADX.'.format(period))；DMI(cls, ohlc: DataFrame, period: int=14, adjust: bool=True): ohlc['up_move'] = ohlc['high'].diff()<br>ohlc['down_move'] = -ohlc['low'].diff()<br>def _dmp(row):<br>    if row['up_move'] > row['down_move'] and row['up_move'] > 0:<br>        return row['up_move']<br>    else:<br>        return 0<br>def _dmn(row):<br>    if row['down_move'] > row['up_move'] and row['down_move'] > 0:<br>        return row['down_move']<br>    else:<br>        return 0<br>ohlc['plus'] = ohlc.apply(_dmp, axis=1)<br>ohlc['minus'] = ohlc.apply(_dmn, axis=1)<br>diplus = pd.Series(100 * (ohlc['plus'] / cls.ATR(ohlc, period)).ewm(alpha=1 / period, adjust=adjust).mean(), name='DI+')<br>diminus = pd.Series(100 * (ohlc['minus'] / cls.ATR(ohlc, period)).ewm(alpha=1 / period, adjust=adjust).mean(), name='DI-')<br>return pd.concat([diplus, diminus], axis=1)；ATR(cls, ohlc: DataFrame, period: int=14): TR = cls.TR(ohlc)<br>return pd.Series(TR.rolling(center=False, window=period).mean(), name='{0} period ATR'.format(period))；TR(cls, ohlc: DataFrame): TR1 = pd.Series(ohlc['high'] - ohlc['low']).abs()<br>TR2 = pd.Series(ohlc['high'] - ohlc['close'].shift()).abs()<br>TR3 = pd.Series(ohlc['close'].shift() - ohlc['low']).abs()<br>_TR = pd.concat([TR1, TR2, TR3], axis=1)<br>_TR['TR'] = _TR.max(axis=1)<br>return pd.Series(_TR['TR'], name='TR')；原目录：ADX（period=14）；追踪：PF00997；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_adx_14d', 'engine': 'finta', 'root_function': 'TA.ADX', 'parameters': {'period': 14, 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_adx_14d', {})
class Factor_finta_adx_14d(PublicFactor):
    name = 'finta_adx_14d'
    description = "固定公开源码默认参数：{'period': 14, 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：ADX(cls, ohlc: DataFrame, period: int=14, adjust: bool=True): dmi = cls.DMI(ohlc, period)<br>return pd.Series(100 * (abs(dmi['DI+'] - dmi['DI-']) / (dmi['DI+'] + dmi['DI-'])).ewm(alpha=1 / period, adjust=adjust).mean(), name='{0} period ADX.'.format(period))；DMI(cls, ohlc: DataFrame, period: int=14, adjust: bool=True): ohlc['up_move'] = ohlc['high'].diff()<br>ohlc['down_move'] = -ohlc['low'].diff()<br>def _dmp(row):<br>    if row['up_move'] > row['down_move'] and row['up_move'] > 0:<br>        return row['up_move']<br>    else:<br>        return 0<br>def _dmn(row):<br>    if row['down_move'] > row['up_move'] and row['down_move'] > 0:<br>        return row['down_move']<br>    else:<br>        return 0<br>ohlc['plus'] = ohlc.apply(_dmp, axis=1)<br>ohlc['minus'] = ohlc.apply(_dmn, axis=1)<br>diplus = pd.Series(100 * (ohlc['plus'] / cls.ATR(ohlc, period)).ewm(alpha=1 / period, adjust=adjust).mean(), name='DI+')<br>diminus = pd.Series(100 * (ohlc['minus'] / cls.ATR(ohlc, period)).ewm(alpha=1 / period, adjust=adjust).mean(), name='DI-')<br>return pd.concat([diplus, diminus], axis=1)；ATR(cls, ohlc: DataFrame, period: int=14): TR = cls.TR(ohlc)<br>return pd.Series(TR.rolling(center=False, window=period).mean(), name='{0} period ATR'.format(period))；TR(cls, ohlc: DataFrame): TR1 = pd.Series(ohlc['high'] - ohlc['low']).abs()<br>TR2 = pd.Series(ohlc['high'] - ohlc['close'].shift()).abs()<br>TR3 = pd.Series(ohlc['close'].shift() - ohlc['low']).abs()<br>_TR = pd.concat([TR1, TR2, TR3], axis=1)<br>_TR['TR'] = _TR.max(axis=1)<br>return pd.Series(_TR['TR'], name='TR')；原目录：ADX（period=14）；追踪：PF00997；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
