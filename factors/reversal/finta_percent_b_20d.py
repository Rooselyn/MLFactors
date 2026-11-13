"""FinTA

公式：固定公开源码默认参数：{'period': 20, 'MA': None, 'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：PERCENT_B(cls, ohlc: DataFrame, period: int=20, MA: Series=None, column: str='close'): BB = TA.BBANDS(ohlc, period, MA, column)<br>percent_b = pd.Series((ohlc['close'] - BB['BB_LOWER']) / (BB['BB_UPPER'] - BB['BB_LOWER']), name='%b')<br>return percent_b；BBANDS(cls, ohlc: DataFrame, period: int=20, MA: Series=None, column: str='close', std_multiplier: float=2): std = ohlc[column].rolling(window=period).std()<br>if not isinstance(MA, pd.core.series.Series):<br>    middle_band = pd.Series(cls.SMA(ohlc, period), name='BB_MIDDLE')<br>else:<br>    middle_band = pd.Series(MA, name='BB_MIDDLE')<br>upper_bb = pd.Series(middle_band + std_multiplier * std, name='BB_UPPER')<br>lower_bb = pd.Series(middle_band - std_multiplier * std, name='BB_LOWER')<br>return pd.concat([upper_bb, middle_band, lower_bb], axis=1)；SMA(cls, ohlc: DataFrame, period: int=41, column: str='close'): return pd.Series(ohlc[column].rolling(window=period).mean(), name='{0} period SMA'.format(period))；原目录：PERCENT_B（period=20, MA=None）；追踪：PF00993；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_percent_b_20d', 'engine': 'finta', 'root_function': 'TA.PERCENT_B', 'parameters': {'period': 20, 'MA': None, 'column': 'close'}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_percent_b_20d', {})
class Factor_finta_percent_b_20d(PublicFactor):
    name = 'finta_percent_b_20d'
    description = "固定公开源码默认参数：{'period': 20, 'MA': None, 'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：PERCENT_B(cls, ohlc: DataFrame, period: int=20, MA: Series=None, column: str='close'): BB = TA.BBANDS(ohlc, period, MA, column)<br>percent_b = pd.Series((ohlc['close'] - BB['BB_LOWER']) / (BB['BB_UPPER'] - BB['BB_LOWER']), name='%b')<br>return percent_b；BBANDS(cls, ohlc: DataFrame, period: int=20, MA: Series=None, column: str='close', std_multiplier: float=2): std = ohlc[column].rolling(window=period).std()<br>if not isinstance(MA, pd.core.series.Series):<br>    middle_band = pd.Series(cls.SMA(ohlc, period), name='BB_MIDDLE')<br>else:<br>    middle_band = pd.Series(MA, name='BB_MIDDLE')<br>upper_bb = pd.Series(middle_band + std_multiplier * std, name='BB_UPPER')<br>lower_bb = pd.Series(middle_band - std_multiplier * std, name='BB_LOWER')<br>return pd.concat([upper_bb, middle_band, lower_bb], axis=1)；SMA(cls, ohlc: DataFrame, period: int=41, column: str='close'): return pd.Series(ohlc[column].rolling(window=period).mean(), name='{0} period SMA'.format(period))；原目录：PERCENT_B（period=20, MA=None）；追踪：PF00993；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
