"""FinTA

公式：固定公开源码默认参数：{'period': 8, 'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：VAMA(cls, ohlcv: DataFrame, period: int=8, column: str='close'): vp = ohlcv['volume'] * ohlcv[column]<br>volsum = ohlcv['volume'].rolling(window=period).mean()<br>volRatio = pd.Series(vp / volsum, name='VAMA')<br>cumSum = (volRatio * ohlcv[column]).rolling(window=period).sum()<br>cumDiv = volRatio.rolling(window=period).sum()<br>return pd.Series(cumSum / cumDiv, name='{0} period VAMA'.format(period))；原目录：VAMA（period=8）；追踪：PF00971；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_vama_8d', 'engine': 'finta', 'root_function': 'TA.VAMA', 'parameters': {'period': 8, 'column': 'close'}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_vama_8d', {})
class Factor_finta_vama_8d(PublicFactor):
    name = 'finta_vama_8d'
    description = "固定公开源码默认参数：{'period': 8, 'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：VAMA(cls, ohlcv: DataFrame, period: int=8, column: str='close'): vp = ohlcv['volume'] * ohlcv[column]<br>volsum = ohlcv['volume'].rolling(window=period).mean()<br>volRatio = pd.Series(vp / volsum, name='VAMA')<br>cumSum = (volRatio * ohlcv[column]).rolling(window=period).sum()<br>cumDiv = volRatio.rolling(window=period).sum()<br>return pd.Series(cumSum / cumDiv, name='{0} period VAMA'.format(period))；原目录：VAMA（period=8）；追踪：PF00971；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
