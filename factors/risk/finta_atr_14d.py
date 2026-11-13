"""FinTA

公式：固定公开源码默认参数：{'period': 14}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：ATR(cls, ohlc: DataFrame, period: int=14): TR = cls.TR(ohlc)<br>return pd.Series(TR.rolling(center=False, window=period).mean(), name='{0} period ATR'.format(period))；TR(cls, ohlc: DataFrame): TR1 = pd.Series(ohlc['high'] - ohlc['low']).abs()<br>TR2 = pd.Series(ohlc['high'] - ohlc['close'].shift()).abs()<br>TR3 = pd.Series(ohlc['close'].shift() - ohlc['low']).abs()<br>_TR = pd.concat([TR1, TR2, TR3], axis=1)<br>_TR['TR'] = _TR.max(axis=1)<br>return pd.Series(_TR['TR'], name='TR')；原目录：ATR（period=14）；追踪：PF00987；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_atr_14d', 'engine': 'finta', 'root_function': 'TA.ATR', 'parameters': {'period': 14}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_atr_14d', {})
class Factor_finta_atr_14d(PublicFactor):
    name = 'finta_atr_14d'
    description = "固定公开源码默认参数：{'period': 14}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：ATR(cls, ohlc: DataFrame, period: int=14): TR = cls.TR(ohlc)<br>return pd.Series(TR.rolling(center=False, window=period).mean(), name='{0} period ATR'.format(period))；TR(cls, ohlc: DataFrame): TR1 = pd.Series(ohlc['high'] - ohlc['low']).abs()<br>TR2 = pd.Series(ohlc['high'] - ohlc['close'].shift()).abs()<br>TR3 = pd.Series(ohlc['close'].shift() - ohlc['low']).abs()<br>_TR = pd.concat([TR1, TR2, TR3], axis=1)<br>_TR['TR'] = _TR.max(axis=1)<br>return pd.Series(_TR['TR'], name='TR')；原目录：ATR（period=14）；追踪：PF00987；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
