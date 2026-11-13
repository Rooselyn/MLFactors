"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._offset=0；self._close=C；self._high=H；self._low=L；self._window=20；self._fillna=False；_run: self._min_periods = 1 if self._fillna else self._window<br>self._hband = self._high.rolling(self._window, min_periods=self._min_periods).max()<br>self._lband = self._low.rolling(self._window, min_periods=self._min_periods).min()；donchian_channel_wband: mavg = self._close.rolling(self._window, min_periods=self._min_periods).mean()<br>wband = (self._hband - self._lband) / mavg * 100<br>wband = self._check_fillna(wband, value=0)<br>if self._offset != 0:<br>    wband = wband.shift(self._offset)<br>return pd.Series(wband, name='dcwband')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：DonchianChannel.donchian_channel_wband（window=20, offset=0）；追踪：PF00901；[来源](https://github.com/bukosabino/ta)。
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
SPEC = {'name': 'ta_donchian_channel_donchian_channel_wband_20d', 'engine': 'ta', 'module': 'volatility', 'class': 'DonchianChannel', 'getter': 'donchian_channel_wband', 'parameters': {'offset': 0, 'window': 20, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_donchian_channel_donchian_channel_wband_20d', {})
class Factor_ta_donchian_channel_donchian_channel_wband_20d(PublicFactor):
    name = 'ta_donchian_channel_donchian_channel_wband_20d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._offset=0；self._close=C；self._high=H；self._low=L；self._window=20；self._fillna=False；_run: self._min_periods = 1 if self._fillna else self._window<br>self._hband = self._high.rolling(self._window, min_periods=self._min_periods).max()<br>self._lband = self._low.rolling(self._window, min_periods=self._min_periods).min()；donchian_channel_wband: mavg = self._close.rolling(self._window, min_periods=self._min_periods).mean()<br>wband = (self._hband - self._lband) / mavg * 100<br>wband = self._check_fillna(wband, value=0)<br>if self._offset != 0:<br>    wband = wband.shift(self._offset)<br>return pd.Series(wband, name='dcwband')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：DonchianChannel.donchian_channel_wband（window=20, offset=0）；追踪：PF00901；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
