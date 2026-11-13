"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=14；self._smooth1=3；self._smooth2=3；self._fillna=False；_run: self._rsi = RSIIndicator(close=self._close, window=self._window, fillna=self._fillna).rsi()<br>lowest_low_rsi = self._rsi.rolling(self._window).min()<br>self._stochrsi = (self._rsi - lowest_low_rsi) / (self._rsi.rolling(self._window).max() - lowest_low_rsi)<br>self._stochrsi_k = self._stochrsi.rolling(self._smooth1).mean()；stochrsi_d: stochrsi_d_series = self._stochrsi_k.rolling(self._smooth2).mean()<br>stochrsi_d_series = self._check_fillna(stochrsi_d_series)<br>return pd.Series(stochrsi_d_series, name='stochrsi_d')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：StochRSIIndicator.stochrsi_d（window=14, smooth1=3, smooth2=3）；追踪：PF00956；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_stoch_rsi_indicator_stochrsi_d_14d', 'engine': 'ta', 'module': 'momentum', 'class': 'StochRSIIndicator', 'getter': 'stochrsi_d', 'parameters': {'window': 14, 'smooth1': 3, 'smooth2': 3, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_stoch_rsi_indicator_stochrsi_d_14d', {})
class Factor_ta_stoch_rsi_indicator_stochrsi_d_14d(PublicFactor):
    name = 'ta_stoch_rsi_indicator_stochrsi_d_14d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=14；self._smooth1=3；self._smooth2=3；self._fillna=False；_run: self._rsi = RSIIndicator(close=self._close, window=self._window, fillna=self._fillna).rsi()<br>lowest_low_rsi = self._rsi.rolling(self._window).min()<br>self._stochrsi = (self._rsi - lowest_low_rsi) / (self._rsi.rolling(self._window).max() - lowest_low_rsi)<br>self._stochrsi_k = self._stochrsi.rolling(self._smooth1).mean()；stochrsi_d: stochrsi_d_series = self._stochrsi_k.rolling(self._smooth2).mean()<br>stochrsi_d_series = self._check_fillna(stochrsi_d_series)<br>return pd.Series(stochrsi_d_series, name='stochrsi_d')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：StochRSIIndicator.stochrsi_d（window=14, smooth1=3, smooth2=3）；追踪：PF00956；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
