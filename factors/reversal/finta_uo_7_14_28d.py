"""FinTA

公式：固定公开源码默认参数：{'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：UO(cls, ohlc: DataFrame, column: str='close'): k = []<br>for row, _row in zip(ohlc.itertuples(), ohlc.shift(1).itertuples()):<br>    k.append(min(row.low, _row.close))<br>bp = pd.Series(ohlc[column] - k, name='bp')<br>Average7 = bp.rolling(window=7).sum() / cls.TR(ohlc).rolling(window=7).sum()<br>Average14 = bp.rolling(window=14).sum() / cls.TR(ohlc).rolling(window=14).sum()<br>Average28 = bp.rolling(window=28).sum() / cls.TR(ohlc).rolling(window=28).sum()<br>return pd.Series(100 * (4 * Average7 + 2 * Average14 + Average28) / (4 + 2 + 1))；TR(cls, ohlc: DataFrame): TR1 = pd.Series(ohlc['high'] - ohlc['low']).abs()<br>TR2 = pd.Series(ohlc['high'] - ohlc['close'].shift()).abs()<br>TR3 = pd.Series(ohlc['close'].shift() - ohlc['low']).abs()<br>_TR = pd.concat([TR1, TR2, TR3], axis=1)<br>_TR['TR'] = _TR.max(axis=1)<br>return pd.Series(_TR['TR'], name='TR')；原目录：UO（无固定窗口）；追踪：PF01002；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_uo_7_14_28d', 'engine': 'finta', 'root_function': 'TA.UO', 'parameters': {'column': 'close'}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_uo_7_14_28d', {})
class Factor_finta_uo_7_14_28d(PublicFactor):
    name = 'finta_uo_7_14_28d'
    description = "固定公开源码默认参数：{'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：UO(cls, ohlc: DataFrame, column: str='close'): k = []<br>for row, _row in zip(ohlc.itertuples(), ohlc.shift(1).itertuples()):<br>    k.append(min(row.low, _row.close))<br>bp = pd.Series(ohlc[column] - k, name='bp')<br>Average7 = bp.rolling(window=7).sum() / cls.TR(ohlc).rolling(window=7).sum()<br>Average14 = bp.rolling(window=14).sum() / cls.TR(ohlc).rolling(window=14).sum()<br>Average28 = bp.rolling(window=28).sum() / cls.TR(ohlc).rolling(window=28).sum()<br>return pd.Series(100 * (4 * Average7 + 2 * Average14 + Average28) / (4 + 2 + 1))；TR(cls, ohlc: DataFrame): TR1 = pd.Series(ohlc['high'] - ohlc['low']).abs()<br>TR2 = pd.Series(ohlc['high'] - ohlc['close'].shift()).abs()<br>TR3 = pd.Series(ohlc['close'].shift() - ohlc['low']).abs()<br>_TR = pd.concat([TR1, TR2, TR3], axis=1)<br>_TR['TR'] = _TR.max(axis=1)<br>return pd.Series(_TR['TR'], name='TR')；原目录：UO（无固定窗口）；追踪：PF01002；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
