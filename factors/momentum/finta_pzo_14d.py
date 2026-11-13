"""FinTA

公式：固定公开源码默认参数：{'period': 14, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：PZO(cls, ohlc: DataFrame, period: int=14, column: str='close', adjust: bool=True): sign = lambda a: (a > 0) - (a < 0)<br>r = ohlc[column].diff().apply(sign) * ohlc[column]<br>cp = pd.Series(r.ewm(span=period, adjust=adjust).mean())<br>tc = cls.EMA(ohlc, period)<br>return pd.Series(100 * (cp / tc), name='{} period PZO'.format(period))；EMA(cls, ohlc: DataFrame, period: int=9, column: str='close', adjust: bool=True): return pd.Series(ohlc[column].ewm(span=period, adjust=adjust).mean(), name='{0} period EMA'.format(period))；原目录：PZO（period=14）；追踪：PF01012；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_pzo_14d', 'engine': 'finta', 'root_function': 'TA.PZO', 'parameters': {'period': 14, 'column': 'close', 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_pzo_14d', {})
class Factor_finta_pzo_14d(PublicFactor):
    name = 'finta_pzo_14d'
    description = "固定公开源码默认参数：{'period': 14, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：PZO(cls, ohlc: DataFrame, period: int=14, column: str='close', adjust: bool=True): sign = lambda a: (a > 0) - (a < 0)<br>r = ohlc[column].diff().apply(sign) * ohlc[column]<br>cp = pd.Series(r.ewm(span=period, adjust=adjust).mean())<br>tc = cls.EMA(ohlc, period)<br>return pd.Series(100 * (cp / tc), name='{} period PZO'.format(period))；EMA(cls, ohlc: DataFrame, period: int=9, column: str='close', adjust: bool=True): return pd.Series(ohlc[column].ewm(span=period, adjust=adjust).mean(), name='{0} period EMA'.format(period))；原目录：PZO（period=14）；追踪：PF01012；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
