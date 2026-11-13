"""FinTA

公式：固定公开源码默认参数：{}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：ADL(cls, ohlcv: DataFrame): MFM = pd.Series((ohlcv['close'] - ohlcv['low'] - (ohlcv['high'] - ohlcv['close'])) / (ohlcv['high'] - ohlcv['low']), name='MFM')<br>MFV = pd.Series(MFM * ohlcv['volume'], name='MFV')<br>return MFV.cumsum()；原目录：ADL（无固定窗口）；追踪：PF01007；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_adl_alld', 'engine': 'finta', 'root_function': 'TA.ADL', 'parameters': {}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_adl_alld', {})
class Factor_finta_adl_alld(PublicFactor):
    name = 'finta_adl_alld'
    description = "固定公开源码默认参数：{}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：ADL(cls, ohlcv: DataFrame): MFM = pd.Series((ohlcv['close'] - ohlcv['low'] - (ohlcv['high'] - ohlcv['close'])) / (ohlcv['high'] - ohlcv['low']), name='MFM')<br>MFV = pd.Series(MFM * ohlcv['volume'], name='MFV')<br>return MFV.cumsum()；原目录：ADL（无固定窗口）；追踪：PF01007；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
