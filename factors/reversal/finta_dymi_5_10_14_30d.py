"""FinTA

公式：固定公开源码默认参数：{'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：DYMI(cls, ohlc: DataFrame, column: str='close', adjust: bool=True): def _get_time(close):<br>    sd = close.rolling(5).std()<br>    asd = sd.rolling(10).mean()<br>    v = sd / asd<br>    t = 14 / v.round()<br>    t[t.isna()] = 0<br>    t = t.map(lambda x: int(min(max(x, 5), 30)))<br>    return t<br>def _dmi(index):<br>    time = t.iloc[index]<br>    if index - time < 0:<br>        subset = ohlc.iloc[0:index]<br>    else:<br>        subset = ohlc.iloc[index - time:index]<br>    return cls.RSI(subset, period=time, adjust=adjust).values[-1]<br>dates = Series(ohlc.index)<br>periods = Series(range(14, len(dates)), index=ohlc.index[14:].values)<br>t = _get_time(ohlc[column])<br>return periods.map(lambda x: _dmi(x))；RSI(cls, ohlc: DataFrame, period: int=14, column: str='close', adjust: bool=True): delta = ohlc[column].diff()<br>up, down = (delta.copy(), delta.copy())<br>up[up < 0] = 0<br>down[down > 0] = 0<br>_gain = up.ewm(alpha=1.0 / period, adjust=adjust).mean()<br>_loss = down.abs().ewm(alpha=1.0 / period, adjust=adjust).mean()<br>RS = _gain / _loss<br>return pd.Series(100 - 100 / (1 + RS), name='{0} period RSI'.format(period))；原目录：DYMI（无固定窗口）；追踪：PF00986；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_dymi_5_10_14_30d', 'engine': 'finta', 'root_function': 'TA.DYMI', 'parameters': {'column': 'close', 'adjust': True}, 'output_index': 0, 'minimum': 30}

@register_factor
@fixed_factor('finta_dymi_5_10_14_30d', {})
class Factor_finta_dymi_5_10_14_30d(PublicFactor):
    name = 'finta_dymi_5_10_14_30d'
    description = "固定公开源码默认参数：{'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：DYMI(cls, ohlc: DataFrame, column: str='close', adjust: bool=True): def _get_time(close):<br>    sd = close.rolling(5).std()<br>    asd = sd.rolling(10).mean()<br>    v = sd / asd<br>    t = 14 / v.round()<br>    t[t.isna()] = 0<br>    t = t.map(lambda x: int(min(max(x, 5), 30)))<br>    return t<br>def _dmi(index):<br>    time = t.iloc[index]<br>    if index - time < 0:<br>        subset = ohlc.iloc[0:index]<br>    else:<br>        subset = ohlc.iloc[index - time:index]<br>    return cls.RSI(subset, period=time, adjust=adjust).values[-1]<br>dates = Series(ohlc.index)<br>periods = Series(range(14, len(dates)), index=ohlc.index[14:].values)<br>t = _get_time(ohlc[column])<br>return periods.map(lambda x: _dmi(x))；RSI(cls, ohlc: DataFrame, period: int=14, column: str='close', adjust: bool=True): delta = ohlc[column].diff()<br>up, down = (delta.copy(), delta.copy())<br>up[up < 0] = 0<br>down[down > 0] = 0<br>_gain = up.ewm(alpha=1.0 / period, adjust=adjust).mean()<br>_loss = down.abs().ewm(alpha=1.0 / period, adjust=adjust).mean()<br>RS = _gain / _loss<br>return pd.Series(100 - 100 / (1 + RS), name='{0} period RSI'.format(period))；原目录：DYMI（无固定窗口）；追踪：PF00986；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
