"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=10；self._pow1=2；self._pow2=30；self._fillna=False；_run: close_values = self._close.values<br>vol = pd.Series(abs(self._close - np.roll(self._close, 1)))<br>min_periods = 0 if self._fillna else self._window<br>er_num = abs(close_values - np.roll(close_values, self._window))<br>er_den = vol.rolling(self._window, min_periods=min_periods).sum()<br>efficiency_ratio = np.divide(er_num, er_den, out=np.zeros_like(er_num), where=er_den != 0)<br>smoothing_constant = ((efficiency_ratio * (2.0 / (self._pow1 + 1) - 2.0 / (self._pow2 + 1.0)) + 2 / (self._pow2 + 1.0)) ** 2.0).values<br>self._kama = np.zeros(smoothing_constant.size)<br>len_kama = len(self._kama)<br>first_value = True<br>for i in range(len_kama):<br>    if np.isnan(smoothing_constant[i]):<br>        self._kama[i] = np.nan<br>    elif first_value:<br>        self._kama[i] = close_values[i]<br>        first_value = False<br>    else:<br>        self._kama[i] = self._kama[i - 1] + smoothing_constant[i] * (close_values[i] - self._kama[i - 1])；kama: kama_series = pd.Series(self._kama, index=self._close.index)<br>kama_series = self._check_fillna(kama_series, value=self._close)<br>return pd.Series(kama_series, name='kama')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：KAMAIndicator.kama（window=10, pow1=2, pow2=30）；追踪：PF00952；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_kama_indicator_kama_10d', 'engine': 'ta', 'module': 'momentum', 'class': 'KAMAIndicator', 'getter': 'kama', 'parameters': {'window': 10, 'pow1': 2, 'pow2': 30, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_kama_indicator_kama_10d', {})
class Factor_ta_kama_indicator_kama_10d(PublicFactor):
    name = 'ta_kama_indicator_kama_10d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=10；self._pow1=2；self._pow2=30；self._fillna=False；_run: close_values = self._close.values<br>vol = pd.Series(abs(self._close - np.roll(self._close, 1)))<br>min_periods = 0 if self._fillna else self._window<br>er_num = abs(close_values - np.roll(close_values, self._window))<br>er_den = vol.rolling(self._window, min_periods=min_periods).sum()<br>efficiency_ratio = np.divide(er_num, er_den, out=np.zeros_like(er_num), where=er_den != 0)<br>smoothing_constant = ((efficiency_ratio * (2.0 / (self._pow1 + 1) - 2.0 / (self._pow2 + 1.0)) + 2 / (self._pow2 + 1.0)) ** 2.0).values<br>self._kama = np.zeros(smoothing_constant.size)<br>len_kama = len(self._kama)<br>first_value = True<br>for i in range(len_kama):<br>    if np.isnan(smoothing_constant[i]):<br>        self._kama[i] = np.nan<br>    elif first_value:<br>        self._kama[i] = close_values[i]<br>        first_value = False<br>    else:<br>        self._kama[i] = self._kama[i - 1] + smoothing_constant[i] * (close_values[i] - self._kama[i - 1])；kama: kama_series = pd.Series(self._kama, index=self._close.index)<br>kama_series = self._check_fillna(kama_series, value=self._close)<br>return pd.Series(kama_series, name='kama')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：KAMAIndicator.kama（window=10, pow1=2, pow2=30）；追踪：PF00952；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
