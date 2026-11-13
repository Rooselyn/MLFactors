"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._close=C；self._window=20；self._window_atr=10；self._fillna=False；self._original_version=True；self._multiplier=2；_run: min_periods = 1 if self._fillna else self._window<br>if self._original_version:<br>    self._tp = ((self._high + self._low + self._close) / 3.0).rolling(self._window, min_periods=min_periods).mean()<br>    self._tp_high = ((4 * self._high - 2 * self._low + self._close) / 3.0).rolling(self._window, min_periods=0).mean()<br>    self._tp_low = ((-2 * self._high + 4 * self._low + self._close) / 3.0).rolling(self._window, min_periods=0).mean()<br>else:<br>    self._tp = self._close.ewm(span=self._window, min_periods=min_periods, adjust=False).mean()<br>    atr = AverageTrueRange(close=self._close, high=self._high, low=self._low, window=self._window_atr, fillna=self._fillna).average_true_range()<br>    self._tp_high = self._tp + self._multiplier * atr<br>    self._tp_low = self._tp - self._multiplier * atr；keltner_channel_wband: wband = (self._tp_high - self._tp_low) / self._tp * 100<br>wband = self._check_fillna(wband, value=0)<br>return pd.Series(wband, name='bbiwband')；辅助算子 _true_range(high: pd.Series, low: pd.Series, prev_close: pd.Series): tr1 = high - low<br>tr2 = (high - prev_close).abs()<br>tr3 = (low - prev_close).abs()<br>true_range = pd.DataFrame(data={'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)<br>return true_range；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：KeltnerChannel.keltner_channel_wband（window=20, window_atr=10, original_version=True, multiplier=2）；追踪：PF00897；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_keltner_channel_keltner_channel_wband_20_10d', 'engine': 'ta', 'module': 'volatility', 'class': 'KeltnerChannel', 'getter': 'keltner_channel_wband', 'parameters': {'window': 20, 'window_atr': 10, 'fillna': False, 'original_version': True, 'multiplier': 2}, 'minimum': 1}

@register_factor
@fixed_factor('ta_keltner_channel_keltner_channel_wband_20_10d', {})
class Factor_ta_keltner_channel_keltner_channel_wband_20_10d(PublicFactor):
    name = 'ta_keltner_channel_keltner_channel_wband_20_10d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._close=C；self._window=20；self._window_atr=10；self._fillna=False；self._original_version=True；self._multiplier=2；_run: min_periods = 1 if self._fillna else self._window<br>if self._original_version:<br>    self._tp = ((self._high + self._low + self._close) / 3.0).rolling(self._window, min_periods=min_periods).mean()<br>    self._tp_high = ((4 * self._high - 2 * self._low + self._close) / 3.0).rolling(self._window, min_periods=0).mean()<br>    self._tp_low = ((-2 * self._high + 4 * self._low + self._close) / 3.0).rolling(self._window, min_periods=0).mean()<br>else:<br>    self._tp = self._close.ewm(span=self._window, min_periods=min_periods, adjust=False).mean()<br>    atr = AverageTrueRange(close=self._close, high=self._high, low=self._low, window=self._window_atr, fillna=self._fillna).average_true_range()<br>    self._tp_high = self._tp + self._multiplier * atr<br>    self._tp_low = self._tp - self._multiplier * atr；keltner_channel_wband: wband = (self._tp_high - self._tp_low) / self._tp * 100<br>wband = self._check_fillna(wband, value=0)<br>return pd.Series(wband, name='bbiwband')；辅助算子 _true_range(high: pd.Series, low: pd.Series, prev_close: pd.Series): tr1 = high - low<br>tr2 = (high - prev_close).abs()<br>tr3 = (low - prev_close).abs()<br>true_range = pd.DataFrame(data={'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)<br>return true_range；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：KeltnerChannel.keltner_channel_wband（window=20, window_atr=10, original_version=True, multiplier=2）；追踪：PF00897；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
