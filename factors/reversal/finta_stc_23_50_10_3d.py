"""FinTA

公式：固定公开源码默认参数：{'period_fast': 23, 'period_slow': 50, 'k_period': 10, 'd_period': 3, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：STC(cls, ohlc: DataFrame, period_fast: int=23, period_slow: int=50, k_period: int=10, d_period: int=3, column: str='close', adjust: bool=True): EMA_fast = pd.Series(ohlc[column].ewm(ignore_na=False, span=period_fast, adjust=adjust).mean(), name='EMA_fast')<br>EMA_slow = pd.Series(ohlc[column].ewm(ignore_na=False, span=period_slow, adjust=adjust).mean(), name='EMA_slow')<br>MACD = pd.Series(EMA_fast - EMA_slow, name='MACD')<br>STOK = pd.Series((MACD - MACD.rolling(window=k_period).min()) / (MACD.rolling(window=k_period).max() - MACD.rolling(window=k_period).min()) * 100)<br>STOD = STOK.rolling(window=d_period).mean()<br>STOD_DoubleSmooth = STOD.rolling(window=d_period).mean()<br>return pd.Series(STOD_DoubleSmooth, name='{0} period STC'.format(k_period))；原目录：STC（period_fast=23, period_slow=50, k_period=10, d_period=3）；追踪：PF01032；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_stc_23_50_10_3d', 'engine': 'finta', 'root_function': 'TA.STC', 'parameters': {'period_fast': 23, 'period_slow': 50, 'k_period': 10, 'd_period': 3, 'column': 'close', 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_stc_23_50_10_3d', {})
class Factor_finta_stc_23_50_10_3d(PublicFactor):
    name = 'finta_stc_23_50_10_3d'
    description = "固定公开源码默认参数：{'period_fast': 23, 'period_slow': 50, 'k_period': 10, 'd_period': 3, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：STC(cls, ohlc: DataFrame, period_fast: int=23, period_slow: int=50, k_period: int=10, d_period: int=3, column: str='close', adjust: bool=True): EMA_fast = pd.Series(ohlc[column].ewm(ignore_na=False, span=period_fast, adjust=adjust).mean(), name='EMA_fast')<br>EMA_slow = pd.Series(ohlc[column].ewm(ignore_na=False, span=period_slow, adjust=adjust).mean(), name='EMA_slow')<br>MACD = pd.Series(EMA_fast - EMA_slow, name='MACD')<br>STOK = pd.Series((MACD - MACD.rolling(window=k_period).min()) / (MACD.rolling(window=k_period).max() - MACD.rolling(window=k_period).min()) * 100)<br>STOD = STOK.rolling(window=d_period).mean()<br>STOD_DoubleSmooth = STOD.rolling(window=d_period).mean()<br>return pd.Series(STOD_DoubleSmooth, name='{0} period STC'.format(k_period))；原目录：STC（period_fast=23, period_slow=50, k_period=10, d_period=3）；追踪：PF01032；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
