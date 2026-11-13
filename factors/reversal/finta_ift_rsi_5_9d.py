"""FinTA

公式：固定公开源码默认参数：{'column': 'close', 'rsi_period': 5, 'wma_period': 9}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：IFT_RSI(cls, ohlc: DataFrame, column: str='close', rsi_period: int=5, wma_period: int=9): v1 = pd.Series(0.1 * (cls.RSI(ohlc, rsi_period) - 50), name='v1')<br>d = wma_period * (wma_period + 1) / 2<br>weights = np.arange(1, wma_period + 1)<br>def linear(w):<br><br>    def _compute(x):<br>        return (w * x).sum() / d<br>    return _compute<br>_wma = v1.rolling(wma_period, min_periods=wma_period)<br>v2 = _wma.apply(linear(weights), raw=True)<br>ift = pd.Series((v2 ** 2 - 1) / (v2 ** 2 + 1), name='IFT_RSI')<br>return ift；RSI(cls, ohlc: DataFrame, period: int=14, column: str='close', adjust: bool=True): delta = ohlc[column].diff()<br>up, down = (delta.copy(), delta.copy())<br>up[up < 0] = 0<br>down[down > 0] = 0<br>_gain = up.ewm(alpha=1.0 / period, adjust=adjust).mean()<br>_loss = down.abs().ewm(alpha=1.0 / period, adjust=adjust).mean()<br>RS = _gain / _loss<br>return pd.Series(100 - 100 / (1 + RS), name='{0} period RSI'.format(period))；原目录：IFT_RSI（rsi_period=5, wma_period=9）；追踪：PF00985；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_ift_rsi_5_9d', 'engine': 'finta', 'root_function': 'TA.IFT_RSI', 'parameters': {'column': 'close', 'rsi_period': 5, 'wma_period': 9}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_ift_rsi_5_9d', {})
class Factor_finta_ift_rsi_5_9d(PublicFactor):
    name = 'finta_ift_rsi_5_9d'
    description = "固定公开源码默认参数：{'column': 'close', 'rsi_period': 5, 'wma_period': 9}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：IFT_RSI(cls, ohlc: DataFrame, column: str='close', rsi_period: int=5, wma_period: int=9): v1 = pd.Series(0.1 * (cls.RSI(ohlc, rsi_period) - 50), name='v1')<br>d = wma_period * (wma_period + 1) / 2<br>weights = np.arange(1, wma_period + 1)<br>def linear(w):<br><br>    def _compute(x):<br>        return (w * x).sum() / d<br>    return _compute<br>_wma = v1.rolling(wma_period, min_periods=wma_period)<br>v2 = _wma.apply(linear(weights), raw=True)<br>ift = pd.Series((v2 ** 2 - 1) / (v2 ** 2 + 1), name='IFT_RSI')<br>return ift；RSI(cls, ohlc: DataFrame, period: int=14, column: str='close', adjust: bool=True): delta = ohlc[column].diff()<br>up, down = (delta.copy(), delta.copy())<br>up[up < 0] = 0<br>down[down > 0] = 0<br>_gain = up.ewm(alpha=1.0 / period, adjust=adjust).mean()<br>_loss = down.abs().ewm(alpha=1.0 / period, adjust=adjust).mean()<br>RS = _gain / _loss<br>return pd.Series(100 - 100 / (1 + RS), name='{0} period RSI'.format(period))；原目录：IFT_RSI（rsi_period=5, wma_period=9）；追踪：PF00985；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
