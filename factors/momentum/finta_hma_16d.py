"""FinTA

公式：固定公开源码默认参数：{'period': 16}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：HMA(cls, ohlc: DataFrame, period: int=16): import math<br>half_length = int(period / 2)<br>sqrt_length = int(math.sqrt(period))<br>wmaf = cls.WMA(ohlc, period=half_length)<br>wmas = cls.WMA(ohlc, period=period)<br>ohlc['deltawma'] = 2 * wmaf - wmas<br>hma = cls.WMA(ohlc, column='deltawma', period=sqrt_length)<br>return pd.Series(hma, name='{0} period HMA.'.format(period))；WMA(cls, ohlc: DataFrame, period: int=9, column: str='close'): d = period * (period + 1) / 2<br>weights = np.arange(1, period + 1)<br>def linear(w):<br><br>    def _compute(x):<br>        return (w * x).sum() / d<br>    return _compute<br>_close = ohlc[column].rolling(period, min_periods=period)<br>wma = _close.apply(linear(weights), raw=True)<br>return pd.Series(wma, name='{0} period WMA.'.format(period))；原目录：HMA（period=16）；追踪：PF00974；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_hma_16d', 'engine': 'finta', 'root_function': 'TA.HMA', 'parameters': {'period': 16}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_hma_16d', {})
class Factor_finta_hma_16d(PublicFactor):
    name = 'finta_hma_16d'
    description = "固定公开源码默认参数：{'period': 16}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：HMA(cls, ohlc: DataFrame, period: int=16): import math<br>half_length = int(period / 2)<br>sqrt_length = int(math.sqrt(period))<br>wmaf = cls.WMA(ohlc, period=half_length)<br>wmas = cls.WMA(ohlc, period=period)<br>ohlc['deltawma'] = 2 * wmaf - wmas<br>hma = cls.WMA(ohlc, column='deltawma', period=sqrt_length)<br>return pd.Series(hma, name='{0} period HMA.'.format(period))；WMA(cls, ohlc: DataFrame, period: int=9, column: str='close'): d = period * (period + 1) / 2<br>weights = np.arange(1, period + 1)<br>def linear(w):<br><br>    def _compute(x):<br>        return (w * x).sum() / d<br>    return _compute<br>_close = ohlc[column].rolling(period, min_periods=period)<br>wma = _close.apply(linear(weights), raw=True)<br>return pd.Series(wma, name='{0} period WMA.'.format(period))；原目录：HMA（period=16）；追踪：PF00974；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
