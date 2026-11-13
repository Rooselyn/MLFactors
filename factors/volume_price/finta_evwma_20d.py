"""FinTA

公式：固定公开源码默认参数：{'period': 20}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：EVWMA(cls, ohlcv: DataFrame, period: int=20): vol_sum = ohlcv['volume'].rolling(window=period).sum()<br>x = (vol_sum - ohlcv['volume']) / vol_sum<br>y = ohlcv['volume'] * ohlcv['close'] / vol_sum<br>evwma = [0]<br>for x, y in zip(x.fillna(0).iteritems(), y.iteritems()):<br>    if x[1] == 0 or y[1] == 0:<br>        evwma.append(0)<br>    else:<br>        evwma.append(evwma[-1] * x[1] + y[1])<br>return pd.Series(evwma[1:], index=ohlcv.index, name='{0} period EVWMA.'.format(period))；原目录：EVWMA（period=20）；追踪：PF00975；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_evwma_20d', 'engine': 'finta', 'root_function': 'TA.EVWMA', 'parameters': {'period': 20}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_evwma_20d', {})
class Factor_finta_evwma_20d(PublicFactor):
    name = 'finta_evwma_20d'
    description = "固定公开源码默认参数：{'period': 20}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：EVWMA(cls, ohlcv: DataFrame, period: int=20): vol_sum = ohlcv['volume'].rolling(window=period).sum()<br>x = (vol_sum - ohlcv['volume']) / vol_sum<br>y = ohlcv['volume'] * ohlcv['close'] / vol_sum<br>evwma = [0]<br>for x, y in zip(x.fillna(0).iteritems(), y.iteritems()):<br>    if x[1] == 0 or y[1] == 0:<br>        evwma.append(0)<br>    else:<br>        evwma.append(evwma[-1] * x[1] + y[1])<br>return pd.Series(evwma[1:], index=ohlcv.index, name='{0} period EVWMA.'.format(period))；原目录：EVWMA（period=20）；追踪：PF00975；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
