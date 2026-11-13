"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=20；self._window_dev=2；self._fillna=False；_run: min_periods = 0 if self._fillna else self._window<br>self._mavg = self._close.rolling(self._window, min_periods=min_periods).mean()<br>self._mstd = self._close.rolling(self._window, min_periods=min_periods).std(ddof=0)<br>self._hband = self._mavg + self._window_dev * self._mstd<br>self._lband = self._mavg - self._window_dev * self._mstd；bollinger_hband_indicator: hband = pd.Series(np.where(self._close > self._hband, 1.0, 0.0), index=self._close.index)<br>hband = self._check_fillna(hband, value=0)<br>return pd.Series(hband, index=self._close.index, name='bbihband')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：BollingerBands.bollinger_hband_indicator（window=20, window_dev=2）；追踪：PF00892；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_bollinger_bands_bollinger_hband_indicator_20d', 'engine': 'ta', 'module': 'volatility', 'class': 'BollingerBands', 'getter': 'bollinger_hband_indicator', 'parameters': {'window': 20, 'window_dev': 2, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_bollinger_bands_bollinger_hband_indicator_20d', {})
class Factor_ta_bollinger_bands_bollinger_hband_indicator_20d(PublicFactor):
    name = 'ta_bollinger_bands_bollinger_hband_indicator_20d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=20；self._window_dev=2；self._fillna=False；_run: min_periods = 0 if self._fillna else self._window<br>self._mavg = self._close.rolling(self._window, min_periods=min_periods).mean()<br>self._mstd = self._close.rolling(self._window, min_periods=min_periods).std(ddof=0)<br>self._hband = self._mavg + self._window_dev * self._mstd<br>self._lband = self._mavg - self._window_dev * self._mstd；bollinger_hband_indicator: hband = pd.Series(np.where(self._close > self._hband, 1.0, 0.0), index=self._close.index)<br>hband = self._check_fillna(hband, value=0)<br>return pd.Series(hband, index=self._close.index, name='bbihband')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：BollingerBands.bollinger_hband_indicator（window=20, window_dev=2）；追踪：PF00892；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
