"""FinTA

公式：固定公开源码默认参数：{'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：CFI(cls, ohlcv: DataFrame, column: str='close', adjust: bool=True): fi1 = pd.Series(ohlcv['volume'] * ohlcv[column].diff())<br>cfi = pd.Series(fi1.ewm(ignore_na=False, min_periods=9, span=10, adjust=adjust).mean(), name='CFI')<br>return cfi.cumsum()；原目录：CFI（无固定窗口）；追踪：PF01014；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_cfi_alld', 'engine': 'finta', 'root_function': 'TA.CFI', 'parameters': {'column': 'close', 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_cfi_alld', {})
class Factor_finta_cfi_alld(PublicFactor):
    name = 'finta_cfi_alld'
    description = "固定公开源码默认参数：{'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：CFI(cls, ohlcv: DataFrame, column: str='close', adjust: bool=True): fi1 = pd.Series(ohlcv['volume'] * ohlcv[column].diff())<br>cfi = pd.Series(fi1.ewm(ignore_na=False, min_periods=9, span=10, adjust=adjust).mean(), name='CFI')<br>return cfi.cumsum()；原目录：CFI（无固定窗口）；追踪：PF01014；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
