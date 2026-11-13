"""FinTA

公式：固定公开源码默认参数：{'period': 3, 'stoch_period': 14}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：STOCHD(cls, ohlc: DataFrame, period: int=3, stoch_period: int=14): return pd.Series(cls.STOCH(ohlc, stoch_period).rolling(center=False, window=period).mean(), name='{0} period STOCH %D.'.format(period))；STOCH(cls, ohlc: DataFrame, period: int=14): highest_high = ohlc['high'].rolling(center=False, window=period).max()<br>lowest_low = ohlc['low'].rolling(center=False, window=period).min()<br>STOCH = pd.Series((ohlc['close'] - lowest_low) / (highest_high - lowest_low) * 100, name='{0} period STOCH %K'.format(period))<br>return STOCH；原目录：STOCHD（period=3, stoch_period=14）；追踪：PF01000；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_stochd_3_14d', 'engine': 'finta', 'root_function': 'TA.STOCHD', 'parameters': {'period': 3, 'stoch_period': 14}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_stochd_3_14d', {})
class Factor_finta_stochd_3_14d(PublicFactor):
    name = 'finta_stochd_3_14d'
    description = "固定公开源码默认参数：{'period': 3, 'stoch_period': 14}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：STOCHD(cls, ohlc: DataFrame, period: int=3, stoch_period: int=14): return pd.Series(cls.STOCH(ohlc, stoch_period).rolling(center=False, window=period).mean(), name='{0} period STOCH %D.'.format(period))；STOCH(cls, ohlc: DataFrame, period: int=14): highest_high = ohlc['high'].rolling(center=False, window=period).max()<br>lowest_low = ohlc['low'].rolling(center=False, window=period).min()<br>STOCH = pd.Series((ohlc['close'] - lowest_low) / (highest_high - lowest_low) * 100, name='{0} period STOCH %K'.format(period))<br>return STOCH；原目录：STOCHD（period=3, stoch_period=14）；追踪：PF01000；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
