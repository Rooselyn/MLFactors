"""FinTA

公式：固定公开源码默认参数：{'period': 42, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：SMMA(cls, ohlc: DataFrame, period: int=42, column: str='close', adjust: bool=True): return pd.Series(ohlc[column].ewm(alpha=1 / period, adjust=adjust).mean(), name='SMMA')；原目录：SMMA（period=42）；追踪：PF00977；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_smma_42d', 'engine': 'finta', 'root_function': 'TA.SMMA', 'parameters': {'period': 42, 'column': 'close', 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_smma_42d', {})
class Factor_finta_smma_42d(PublicFactor):
    name = 'finta_smma_42d'
    description = "固定公开源码默认参数：{'period': 42, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：SMMA(cls, ohlc: DataFrame, period: int=42, column: str='close', adjust: bool=True): return pd.Series(ohlc[column].ewm(alpha=1 / period, adjust=adjust).mean(), name='SMMA')；原目录：SMMA（period=42）；追踪：PF00977；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
