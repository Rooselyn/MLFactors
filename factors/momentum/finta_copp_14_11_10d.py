"""FinTA

公式：固定公开源码默认参数：{'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：COPP(cls, ohlc: DataFrame, adjust: bool=True): roc1 = cls.ROC(ohlc, 14)<br>roc2 = cls.ROC(ohlc, 11)<br>return pd.Series((roc1 + roc2).ewm(span=10, min_periods=9, adjust=adjust).mean(), name='Coppock Curve')；ROC(cls, ohlc: DataFrame, period: int=12, column: str='close'): return pd.Series(ohlc[column].diff(period) / ohlc[column].shift(period) * 100, name='ROC')；原目录：COPP（无固定窗口）；追踪：PF01017；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_copp_14_11_10d', 'engine': 'finta', 'root_function': 'TA.COPP', 'parameters': {'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_copp_14_11_10d', {})
class Factor_finta_copp_14_11_10d(PublicFactor):
    name = 'finta_copp_14_11_10d'
    description = "固定公开源码默认参数：{'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：COPP(cls, ohlc: DataFrame, adjust: bool=True): roc1 = cls.ROC(ohlc, 14)<br>roc2 = cls.ROC(ohlc, 11)<br>return pd.Series((roc1 + roc2).ewm(span=10, min_periods=9, adjust=adjust).mean(), name='Coppock Curve')；ROC(cls, ohlc: DataFrame, period: int=12, column: str='close'): return pd.Series(ohlc[column].diff(period) / ohlc[column].shift(period) * 100, name='ROC')；原目录：COPP（无固定窗口）；追踪：PF01017；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
