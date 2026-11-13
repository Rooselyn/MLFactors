"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._high=H；self._low=L；self._window=14；self._smooth_window=3；self._fillna=False；_run: min_periods = 0 if self._fillna else self._window<br>smin = self._low.rolling(self._window, min_periods=min_periods).min()<br>smax = self._high.rolling(self._window, min_periods=min_periods).max()<br>self._stoch_k = 100 * (self._close - smin) / (smax - smin)；stoch_signal: min_periods = 0 if self._fillna else self._smooth_window<br>stoch_d = self._stoch_k.rolling(self._smooth_window, min_periods=min_periods).mean()<br>stoch_d = self._check_fillna(stoch_d, value=50)<br>return pd.Series(stoch_d, name='stoch_k_signal')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：StochasticOscillator.stoch_signal（window=14, smooth_window=3）；追踪：PF00951；[来源](https://github.com/bukosabino/ta)。
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
SPEC = {'name': 'ta_stochastic_oscillator_stoch_signal_14_3d', 'engine': 'ta', 'module': 'momentum', 'class': 'StochasticOscillator', 'getter': 'stoch_signal', 'parameters': {'window': 14, 'smooth_window': 3, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_stochastic_oscillator_stoch_signal_14_3d', {})
class Factor_ta_stochastic_oscillator_stoch_signal_14_3d(PublicFactor):
    name = 'ta_stochastic_oscillator_stoch_signal_14_3d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._high=H；self._low=L；self._window=14；self._smooth_window=3；self._fillna=False；_run: min_periods = 0 if self._fillna else self._window<br>smin = self._low.rolling(self._window, min_periods=min_periods).min()<br>smax = self._high.rolling(self._window, min_periods=min_periods).max()<br>self._stoch_k = 100 * (self._close - smin) / (smax - smin)；stoch_signal: min_periods = 0 if self._fillna else self._smooth_window<br>stoch_d = self._stoch_k.rolling(self._smooth_window, min_periods=min_periods).mean()<br>stoch_d = self._check_fillna(stoch_d, value=50)<br>return pd.Series(stoch_d, name='stoch_k_signal')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：StochasticOscillator.stoch_signal（window=14, smooth_window=3）；追踪：PF00951；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
