"""FinTA

公式：固定公开源码默认参数：{'period': 14, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：RSI(cls, ohlc: DataFrame, period: int=14, column: str='close', adjust: bool=True): delta = ohlc[column].diff()<br>up, down = (delta.copy(), delta.copy())<br>up[up < 0] = 0<br>down[down > 0] = 0<br>_gain = up.ewm(alpha=1.0 / period, adjust=adjust).mean()<br>_loss = down.abs().ewm(alpha=1.0 / period, adjust=adjust).mean()<br>RS = _gain / _loss<br>return pd.Series(100 - 100 / (1 + RS), name='{0} period RSI'.format(period))；原目录：RSI（period=14）；追踪：PF00984；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_rsi_14d', 'engine': 'finta', 'root_function': 'TA.RSI', 'parameters': {'period': 14, 'column': 'close', 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_rsi_14d', {})
class Factor_finta_rsi_14d(PublicFactor):
    name = 'finta_rsi_14d'
    description = "固定公开源码默认参数：{'period': 14, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：RSI(cls, ohlc: DataFrame, period: int=14, column: str='close', adjust: bool=True): delta = ohlc[column].diff()<br>up, down = (delta.copy(), delta.copy())<br>up[up < 0] = 0<br>down[down > 0] = 0<br>_gain = up.ewm(alpha=1.0 / period, adjust=adjust).mean()<br>_loss = down.abs().ewm(alpha=1.0 / period, adjust=adjust).mean()<br>RS = _gain / _loss<br>return pd.Series(100 - 100 / (1 + RS), name='{0} period RSI'.format(period))；原目录：RSI（period=14）；追踪：PF00984；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
