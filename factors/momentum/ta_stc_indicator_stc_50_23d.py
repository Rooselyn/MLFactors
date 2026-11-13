"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window_slow=50；self._window_fast=23；self._cycle=10；self._smooth1=3；self._smooth2=3；self._fillna=False；_run: _emafast = _ema(self._close, self._window_fast, self._fillna)<br>_emaslow = _ema(self._close, self._window_slow, self._fillna)<br>_macd = _emafast - _emaslow<br>_macdmin = _macd.rolling(window=self._cycle).min()<br>_macdmax = _macd.rolling(window=self._cycle).max()<br>_stoch_k = 100 * (_macd - _macdmin) / (_macdmax - _macdmin)<br>_stoch_d = _ema(_stoch_k, self._smooth1, self._fillna)<br>_stoch_d_min = _stoch_d.rolling(window=self._cycle).min()<br>_stoch_d_max = _stoch_d.rolling(window=self._cycle).max()<br>_stoch_kd = 100 * (_stoch_d - _stoch_d_min) / (_stoch_d_max - _stoch_d_min)<br>self._stc = _ema(_stoch_kd, self._smooth2, self._fillna)；stc: stc_series = self._check_fillna(self._stc)<br>return pd.Series(stc_series, name='stc')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：STCIndicator.stc（window_slow=50, window_fast=23, cycle=10, smooth1=3, smooth2=3）；追踪：PF00935；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_stc_indicator_stc_50_23d', 'engine': 'ta', 'module': 'trend', 'class': 'STCIndicator', 'getter': 'stc', 'parameters': {'window_slow': 50, 'window_fast': 23, 'cycle': 10, 'smooth1': 3, 'smooth2': 3, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_stc_indicator_stc_50_23d', {})
class Factor_ta_stc_indicator_stc_50_23d(PublicFactor):
    name = 'ta_stc_indicator_stc_50_23d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window_slow=50；self._window_fast=23；self._cycle=10；self._smooth1=3；self._smooth2=3；self._fillna=False；_run: _emafast = _ema(self._close, self._window_fast, self._fillna)<br>_emaslow = _ema(self._close, self._window_slow, self._fillna)<br>_macd = _emafast - _emaslow<br>_macdmin = _macd.rolling(window=self._cycle).min()<br>_macdmax = _macd.rolling(window=self._cycle).max()<br>_stoch_k = 100 * (_macd - _macdmin) / (_macdmax - _macdmin)<br>_stoch_d = _ema(_stoch_k, self._smooth1, self._fillna)<br>_stoch_d_min = _stoch_d.rolling(window=self._cycle).min()<br>_stoch_d_max = _stoch_d.rolling(window=self._cycle).max()<br>_stoch_kd = 100 * (_stoch_d - _stoch_d_min) / (_stoch_d_max - _stoch_d_min)<br>self._stc = _ema(_stoch_kd, self._smooth2, self._fillna)；stc: stc_series = self._check_fillna(self._stc)<br>return pd.Series(stc_series, name='stc')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：STCIndicator.stc（window_slow=50, window_fast=23, cycle=10, smooth1=3, smooth2=3）；追踪：PF00935；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
