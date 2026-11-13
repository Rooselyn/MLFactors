"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window_slow=25；self._window_fast=13；self._fillna=False；_run: diff_close = self._close - self._close.shift(1)<br>min_periods_r = 0 if self._fillna else self._window_slow<br>min_periods_s = 0 if self._fillna else self._window_fast<br>smoothed = diff_close.ewm(span=self._window_slow, min_periods=min_periods_r, adjust=False).mean().ewm(span=self._window_fast, min_periods=min_periods_s, adjust=False).mean()<br>smoothed_abs = abs(diff_close).ewm(span=self._window_slow, min_periods=min_periods_r, adjust=False).mean().ewm(span=self._window_fast, min_periods=min_periods_s, adjust=False).mean()<br>self._tsi = smoothed / smoothed_abs<br>self._tsi *= 100；tsi: tsi_series = self._check_fillna(self._tsi, value=0)<br>return pd.Series(tsi_series, name='tsi')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：TSIIndicator.tsi（window_slow=25, window_fast=13）；追踪：PF00948；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_tsi_indicator_tsi_25_13d', 'engine': 'ta', 'module': 'momentum', 'class': 'TSIIndicator', 'getter': 'tsi', 'parameters': {'window_slow': 25, 'window_fast': 13, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_tsi_indicator_tsi_25_13d', {})
class Factor_ta_tsi_indicator_tsi_25_13d(PublicFactor):
    name = 'ta_tsi_indicator_tsi_25_13d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window_slow=25；self._window_fast=13；self._fillna=False；_run: diff_close = self._close - self._close.shift(1)<br>min_periods_r = 0 if self._fillna else self._window_slow<br>min_periods_s = 0 if self._fillna else self._window_fast<br>smoothed = diff_close.ewm(span=self._window_slow, min_periods=min_periods_r, adjust=False).mean().ewm(span=self._window_fast, min_periods=min_periods_s, adjust=False).mean()<br>smoothed_abs = abs(diff_close).ewm(span=self._window_slow, min_periods=min_periods_r, adjust=False).mean().ewm(span=self._window_fast, min_periods=min_periods_s, adjust=False).mean()<br>self._tsi = smoothed / smoothed_abs<br>self._tsi *= 100；tsi: tsi_series = self._check_fillna(self._tsi, value=0)<br>return pd.Series(tsi_series, name='tsi')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：TSIIndicator.tsi（window_slow=25, window_fast=13）；追踪：PF00948；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
