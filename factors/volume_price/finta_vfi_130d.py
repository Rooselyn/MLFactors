"""FinTA

公式：固定公开源码默认参数：{'period': 130, 'smoothing_factor': 3, 'factor': 0.2, 'vfactor': 2.5, 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：VFI(cls, ohlc: DataFrame, period: int=130, smoothing_factor: int=3, factor: int=0.2, vfactor: int=2.5, adjust: bool=True): typical = TA.TP(ohlc)<br>inter = typical.apply(np.log).diff()<br>vinter = inter.rolling(window=30).std()<br>cutoff = pd.Series(factor * vinter * ohlc['close'], name='cutoff')<br>price_change = pd.Series(typical.diff(), name='pc')<br>mav = pd.Series(ohlc['volume'].rolling(center=False, window=period).mean(), name='mav')<br>_va = pd.concat([ohlc['volume'], mav.shift()], axis=1)<br>_mp = pd.concat([price_change, cutoff], axis=1)<br>_mp.fillna(value=0, inplace=True)<br>def _vol_added(row):<br>    \"\"\" Determine the maximum volume to be added\"\"\"<br>    if row['volume'] > vfactor * row['mav']:<br>        return vfactor * row['mav']<br>    else:<br>        return row['volume']<br>added_vol = _va.apply(_vol_added, axis=1)<br>def _multiplier(row):<br>    \"\"\"<br>            Determine whether the volume is up volume (multiplier +1) or<br>            down volume (multiplier -1). If price change is smaller than cutoff<br>            do not count volume (multipler 0).<br>            \"\"\"<br>    if row['pc'] > row['cutoff']:<br>        return 1<br>    elif row['pc'] < 0 - row['cutoff']:<br>        return -1<br>    else:<br>        return 0<br>multiplier = _mp.apply(_multiplier, axis=1)<br>raw_sum = (multiplier * added_vol).rolling(window=period).sum()<br>raw_value = raw_sum / mav.shift()<br>vfi = pd.Series(raw_value.ewm(ignore_na=False, min_periods=smoothing_factor - 1, span=smoothing_factor, adjust=adjust).mean(), name='VFI')<br>return vfi；TP(cls, ohlc: DataFrame): return pd.Series((ohlc['high'] + ohlc['low'] + ohlc['close']) / 3, name='TP')；原目录：VFI（period=130, smoothing_factor=3, factor=0.2, vfactor=2.5）；追踪：PF01030；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_vfi_130d', 'engine': 'finta', 'root_function': 'TA.VFI', 'parameters': {'period': 130, 'smoothing_factor': 3, 'factor': 0.2, 'vfactor': 2.5, 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_vfi_130d', {})
class Factor_finta_vfi_130d(PublicFactor):
    name = 'finta_vfi_130d'
    description = '固定公开源码默认参数：{\'period\': 130, \'smoothing_factor\': 3, \'factor\': 0.2, \'vfactor\': 2.5, \'adjust\': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：VFI(cls, ohlc: DataFrame, period: int=130, smoothing_factor: int=3, factor: int=0.2, vfactor: int=2.5, adjust: bool=True): typical = TA.TP(ohlc)<br>inter = typical.apply(np.log).diff()<br>vinter = inter.rolling(window=30).std()<br>cutoff = pd.Series(factor * vinter * ohlc[\'close\'], name=\'cutoff\')<br>price_change = pd.Series(typical.diff(), name=\'pc\')<br>mav = pd.Series(ohlc[\'volume\'].rolling(center=False, window=period).mean(), name=\'mav\')<br>_va = pd.concat([ohlc[\'volume\'], mav.shift()], axis=1)<br>_mp = pd.concat([price_change, cutoff], axis=1)<br>_mp.fillna(value=0, inplace=True)<br>def _vol_added(row):<br>    """ Determine the maximum volume to be added"""<br>    if row[\'volume\'] > vfactor * row[\'mav\']:<br>        return vfactor * row[\'mav\']<br>    else:<br>        return row[\'volume\']<br>added_vol = _va.apply(_vol_added, axis=1)<br>def _multiplier(row):<br>    """<br>            Determine whether the volume is up volume (multiplier +1) or<br>            down volume (multiplier -1). If price change is smaller than cutoff<br>            do not count volume (multipler 0).<br>            """<br>    if row[\'pc\'] > row[\'cutoff\']:<br>        return 1<br>    elif row[\'pc\'] < 0 - row[\'cutoff\']:<br>        return -1<br>    else:<br>        return 0<br>multiplier = _mp.apply(_multiplier, axis=1)<br>raw_sum = (multiplier * added_vol).rolling(window=period).sum()<br>raw_value = raw_sum / mav.shift()<br>vfi = pd.Series(raw_value.ewm(ignore_na=False, min_periods=smoothing_factor - 1, span=smoothing_factor, adjust=adjust).mean(), name=\'VFI\')<br>return vfi；TP(cls, ohlc: DataFrame): return pd.Series((ohlc[\'high\'] + ohlc[\'low\'] + ohlc[\'close\']) / 3, name=\'TP\')；原目录：VFI（period=130, smoothing_factor=3, factor=0.2, vfactor=2.5）；追踪：PF01030；[来源](https://github.com/peerchemist/finta)。'
    INPUTS = INPUTS
    SPEC = SPEC
