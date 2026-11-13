"""FinTA

公式：固定公开源码默认参数：{'period': 9, 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：MI(cls, ohlc: DataFrame, period: int=9, adjust: bool=True): _range = pd.Series(ohlc['high'] - ohlc['low'], name='range')<br>EMA9 = _range.ewm(span=period, ignore_na=False, adjust=adjust).mean()<br>DEMA9 = EMA9.ewm(span=period, ignore_na=False, adjust=adjust).mean()<br>mass = EMA9 / DEMA9<br>return pd.Series(mass.rolling(window=25).sum(), name='Mass Index')；原目录：MI（period=9）；追踪：PF01003；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_mi_9d', 'engine': 'finta', 'root_function': 'TA.MI', 'parameters': {'period': 9, 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_mi_9d', {})
class Factor_finta_mi_9d(PublicFactor):
    name = 'finta_mi_9d'
    description = "固定公开源码默认参数：{'period': 9, 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：MI(cls, ohlc: DataFrame, period: int=9, adjust: bool=True): _range = pd.Series(ohlc['high'] - ohlc['low'], name='range')<br>EMA9 = _range.ewm(span=period, ignore_na=False, adjust=adjust).mean()<br>DEMA9 = EMA9.ewm(span=period, ignore_na=False, adjust=adjust).mean()<br>mass = EMA9 / DEMA9<br>return pd.Series(mass.rolling(window=25).sum(), name='Mass Index')；原目录：MI（period=9）；追踪：PF01003；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
