"""FinTA

公式：固定公开源码默认参数：{'period': 26, 'adjust': True, 'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：ZLEMA(cls, ohlc: DataFrame, period: int=26, adjust: bool=True, column: str='close'): lag = (period - 1) / 2<br>ema = pd.Series(ohlc[column] + ohlc[column].diff(lag), name='{0} period ZLEMA.'.format(period))<br>zlema = pd.Series(ema.ewm(span=period, adjust=adjust).mean(), name='{0} period ZLEMA'.format(period))<br>return zlema；原目录：ZLEMA（period=26）；追踪：PF00973；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_zlema_26d', 'engine': 'finta', 'root_function': 'TA.ZLEMA', 'parameters': {'period': 26, 'adjust': True, 'column': 'close'}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_zlema_26d', {})
class Factor_finta_zlema_26d(PublicFactor):
    name = 'finta_zlema_26d'
    description = "固定公开源码默认参数：{'period': 26, 'adjust': True, 'column': 'close'}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：ZLEMA(cls, ohlc: DataFrame, period: int=26, adjust: bool=True, column: str='close'): lag = (period - 1) / 2<br>ema = pd.Series(ohlc[column] + ohlc[column].diff(lag), name='{0} period ZLEMA.'.format(period))<br>zlema = pd.Series(ema.ewm(span=period, adjust=adjust).mean(), name='{0} period ZLEMA'.format(period))<br>return zlema；原目录：ZLEMA（period=26）；追踪：PF00973；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
