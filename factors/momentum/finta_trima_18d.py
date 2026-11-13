"""FinTA

公式：固定公开源码默认参数：{'period': 18}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：TRIMA(cls, ohlc: DataFrame, period: int=18): SMA = cls.SMA(ohlc, period).rolling(window=period).sum()<br>return pd.Series(SMA / period, name='{0} period TRIMA'.format(period))；SMA(cls, ohlc: DataFrame, period: int=41, column: str='close'): return pd.Series(ohlc[column].rolling(window=period).mean(), name='{0} period SMA'.format(period))；原目录：TRIMA（period=18）；追踪：PF00969；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_trima_18d', 'engine': 'finta', 'root_function': 'TA.TRIMA', 'parameters': {'period': 18}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_trima_18d', {})
class Factor_finta_trima_18d(PublicFactor):
    name = 'finta_trima_18d'
    description = "固定公开源码默认参数：{'period': 18}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：TRIMA(cls, ohlc: DataFrame, period: int=18): SMA = cls.SMA(ohlc, period).rolling(window=period).sum()<br>return pd.Series(SMA / period, name='{0} period TRIMA'.format(period))；SMA(cls, ohlc: DataFrame, period: int=41, column: str='close'): return pd.Series(ohlc[column].rolling(window=period).mean(), name='{0} period SMA'.format(period))；原目录：TRIMA（period=18）；追踪：PF00969；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
