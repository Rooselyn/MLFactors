"""FinTA

公式：固定公开源码默认参数：{'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：OBV(cls, ohlcv: DataFrame, column: str='close'): ohlcv['OBV'] = np.nan<br>neg_change = ohlcv[column] < ohlcv[column].shift(1)<br>pos_change = ohlcv[column] >= ohlcv[column].shift(1)<br>no_change = ohlcv[column] == ohlcv[column].shift(1)<br>if pos_change.any():<br>    ohlcv.loc[pos_change, 'OBV'] = ohlcv['volume']<br>if neg_change.any():<br>    ohlcv.loc[neg_change, 'OBV'] = -ohlcv['volume']<br>if no_change.any():<br>    ohlcv.loc[no_change, 'OBV'] = ohlcv['OBV'].shift(1)<br>return pd.Series(ohlcv['OBV'].cumsum(), name='OBV')；原目录：OBV（无固定窗口）；追踪：PF01009；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_obv_alld', 'engine': 'finta', 'root_function': 'TA.OBV', 'parameters': {'column': 'close'}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_obv_alld', {})
class Factor_finta_obv_alld(PublicFactor):
    name = 'finta_obv_alld'
    description = "固定公开源码默认参数：{'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：OBV(cls, ohlcv: DataFrame, column: str='close'): ohlcv['OBV'] = np.nan<br>neg_change = ohlcv[column] < ohlcv[column].shift(1)<br>pos_change = ohlcv[column] >= ohlcv[column].shift(1)<br>no_change = ohlcv[column] == ohlcv[column].shift(1)<br>if pos_change.any():<br>    ohlcv.loc[pos_change, 'OBV'] = ohlcv['volume']<br>if neg_change.any():<br>    ohlcv.loc[neg_change, 'OBV'] = -ohlcv['volume']<br>if no_change.any():<br>    ohlcv.loc[no_change, 'OBV'] = ohlcv['OBV'].shift(1)<br>return pd.Series(ohlcv['OBV'].cumsum(), name='OBV')；原目录：OBV（无固定窗口）；追踪：PF01009；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
