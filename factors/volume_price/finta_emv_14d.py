"""FinTA

公式：固定公开源码默认参数：{'period': 14}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：EMV(cls, ohlcv: Series, period: int=14): distance = pd.Series((ohlcv['high'] + ohlcv['low']) / 2 - (ohlcv['high'].shift() + ohlcv['low'].shift()) / 2)<br>box_ratio = pd.Series(ohlcv['volume'] / 1000000 / (ohlcv['high'] - ohlcv['low']))<br>_emv = pd.Series(distance / box_ratio)<br>return pd.Series(_emv.rolling(window=period).mean(), name='{0} period EMV.'.format(period))；原目录：EMV（period=14）；追踪：PF01016；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_emv_14d', 'engine': 'finta', 'root_function': 'TA.EMV', 'parameters': {'period': 14}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_emv_14d', {})
class Factor_finta_emv_14d(PublicFactor):
    name = 'finta_emv_14d'
    description = "固定公开源码默认参数：{'period': 14}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：EMV(cls, ohlcv: Series, period: int=14): distance = pd.Series((ohlcv['high'] + ohlcv['low']) / 2 - (ohlcv['high'].shift() + ohlcv['low'].shift()) / 2)<br>box_ratio = pd.Series(ohlcv['volume'] / 1000000 / (ohlcv['high'] - ohlcv['low']))<br>_emv = pd.Series(distance / box_ratio)<br>return pd.Series(_emv.rolling(window=period).mean(), name='{0} period EMV.'.format(period))；原目录：EMV（period=14）；追踪：PF01016；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
