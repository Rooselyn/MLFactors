"""FinTA

公式：固定公开源码默认参数：{'period': 13, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：EFI(cls, ohlcv: DataFrame, period: int=13, column: str='close', adjust: bool=True): fi = pd.Series(ohlcv[column].diff() * ohlcv['volume'])<br>return pd.Series(fi.ewm(ignore_na=False, span=period, adjust=adjust).mean(), name='{0} period Force Index'.format(period))；原目录：EFI（period=13）；追踪：PF01013；[来源](https://github.com/peerchemist/finta)。
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
SPEC = {'name': 'finta_efi_13d', 'engine': 'finta', 'root_function': 'TA.EFI', 'parameters': {'period': 13, 'column': 'close', 'adjust': True}, 'output_index': 0, 'minimum': 1}

@register_factor
@fixed_factor('finta_efi_13d', {})
class Factor_finta_efi_13d(PublicFactor):
    name = 'finta_efi_13d'
    description = "固定公开源码默认参数：{'period': 13, 'column': 'close', 'adjust': True}；完整数值递推及依赖（Series/DataFrame仅为本地临时计算结构）：EFI(cls, ohlcv: DataFrame, period: int=13, column: str='close', adjust: bool=True): fi = pd.Series(ohlcv[column].diff() * ohlcv['volume'])<br>return pd.Series(fi.ewm(ignore_na=False, span=period, adjust=adjust).mean(), name='{0} period Force Index'.format(period))；原目录：EFI（period=13）；追踪：PF01013；[来源](https://github.com/peerchemist/finta)。"
    INPUTS = INPUTS
    SPEC = SPEC
