"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._volume=V；self._window=13；self._fillna=False；_run: fi_series = (self._close - self._close.shift(1)) * self._volume<br>self._fi = _ema(fi_series, self._window, fillna=self._fillna)；force_index: fi_series = self._check_fillna(self._fi, value=0)<br>return pd.Series(fi_series, name=f'fi_{self._window}')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：ForceIndexIndicator.force_index（window=13）；追踪：PF00941；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ta_force_index_indicator_force_index_13d', 'engine': 'ta', 'module': 'volume', 'class': 'ForceIndexIndicator', 'getter': 'force_index', 'parameters': {'window': 13, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_force_index_indicator_force_index_13d', {})
class Factor_ta_force_index_indicator_force_index_13d(PublicFactor):
    name = 'ta_force_index_indicator_force_index_13d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._volume=V；self._window=13；self._fillna=False；_run: fi_series = (self._close - self._close.shift(1)) * self._volume<br>self._fi = _ema(fi_series, self._window, fillna=self._fillna)；force_index: fi_series = self._check_fillna(self._fi, value=0)<br>return pd.Series(fi_series, name=f'fi_{self._window}')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：ForceIndexIndicator.force_index（window=13）；追踪：PF00941；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
