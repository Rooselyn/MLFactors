"""FinTA

公式：固定公开源码默认参数：{'period': 14, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：VZO(cls, ohlc: DataFrame, period: int=14, column: str='close', adjust: bool=True): sign = lambda a: (a > 0) - (a < 0)<br>r = ohlc[column].diff().apply(sign) * ohlc['volume']<br>dvma = r.ewm(span=period, adjust=adjust).mean()<br>vma = ohlc['volume'].ewm(span=period, adjust=adjust).mean()<br>return pd.Series(100 * (dvma / vma), name='VZO')；原目录：VZO（period=14）；追踪：PF01011；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_vzo_14d', 'engine': 'finta', 'root_function': 'TA.VZO', 'parameters': {'period': 14, 'column': 'close', 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_vzo_14d', {})
class Factor_finta_vzo_14d(PublicFactor):
    name = 'finta_vzo_14d'
    description = "固定公开源码默认参数：{'period': 14, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：VZO(cls, ohlc: DataFrame, period: int=14, column: str='close', adjust: bool=True): sign = lambda a: (a > 0) - (a < 0)<br>r = ohlc[column].diff().apply(sign) * ohlc['volume']<br>dvma = r.ewm(span=period, adjust=adjust).mean()<br>vma = ohlc['volume'].ewm(span=period, adjust=adjust).mean()<br>return pd.Series(100 * (dvma / vma), name='VZO')；原目录：VZO（period=14）；追踪：PF01011；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
