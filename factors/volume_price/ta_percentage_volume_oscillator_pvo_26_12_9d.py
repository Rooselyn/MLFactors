"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._volume=V；self._window_slow=26；self._window_fast=12；self._window_sign=9；self._fillna=False；_run: _emafast = _ema(self._volume, self._window_fast, self._fillna)<br>_emaslow = _ema(self._volume, self._window_slow, self._fillna)<br>self._pvo = (_emafast - _emaslow) / _emaslow * 100<br>self._pvo_signal = _ema(self._pvo, self._window_sign, self._fillna)<br>self._pvo_hist = self._pvo - self._pvo_signal；pvo: pvo_series = self._check_fillna(self._pvo, value=0)<br>return pd.Series(pvo_series, name=f'PVO_{self._window_fast}_{self._window_slow}')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：PercentageVolumeOscillator.pvo（window_slow=26, window_fast=12, window_sign=9）；追踪：PF00960；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ta_percentage_volume_oscillator_pvo_26_12_9d', 'engine': 'ta', 'module': 'momentum', 'class': 'PercentageVolumeOscillator', 'getter': 'pvo', 'parameters': {'window_slow': 26, 'window_fast': 12, 'window_sign': 9, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_percentage_volume_oscillator_pvo_26_12_9d', {})
class Factor_ta_percentage_volume_oscillator_pvo_26_12_9d(PublicFactor):
    name = 'ta_percentage_volume_oscillator_pvo_26_12_9d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._volume=V；self._window_slow=26；self._window_fast=12；self._window_sign=9；self._fillna=False；_run: _emafast = _ema(self._volume, self._window_fast, self._fillna)<br>_emaslow = _ema(self._volume, self._window_slow, self._fillna)<br>self._pvo = (_emafast - _emaslow) / _emaslow * 100<br>self._pvo_signal = _ema(self._pvo, self._window_sign, self._fillna)<br>self._pvo_hist = self._pvo - self._pvo_signal；pvo: pvo_series = self._check_fillna(self._pvo, value=0)<br>return pd.Series(pvo_series, name=f'PVO_{self._window_fast}_{self._window_slow}')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：PercentageVolumeOscillator.pvo（window_slow=26, window_fast=12, window_sign=9）；追踪：PF00960；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
