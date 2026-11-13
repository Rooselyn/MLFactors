"""FinTA

公式：固定公开源码默认参数：{'period': 20, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：TRIX(cls, ohlc: DataFrame, period: int=20, column: str='close', adjust: bool=True): data = ohlc[column]<br>def _ema(data, period, adjust):<br>    return pd.Series(data.ewm(span=period, adjust=adjust).mean())<br>m = _ema(_ema(_ema(data, period, adjust), period, adjust), period, adjust)<br>return pd.Series(100 * (m.diff() / m), name='{0} period TRIX'.format(period))；原目录：TRIX（period=20）；追踪：PF00970；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_trix_20d', 'engine': 'finta', 'root_function': 'TA.TRIX', 'parameters': {'period': 20, 'column': 'close', 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_trix_20d', {})
class Factor_finta_trix_20d(PublicFactor):
    name = 'finta_trix_20d'
    description = "固定公开源码默认参数：{'period': 20, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：TRIX(cls, ohlc: DataFrame, period: int=20, column: str='close', adjust: bool=True): data = ohlc[column]<br>def _ema(data, period, adjust):<br>    return pd.Series(data.ewm(span=period, adjust=adjust).mean())<br>m = _ema(_ema(_ema(data, period, adjust), period, adjust), period, adjust)<br>return pd.Series(100 * (m.diff() / m), name='{0} period TRIX'.format(period))；原目录：TRIX（period=20）；追踪：PF00970；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
