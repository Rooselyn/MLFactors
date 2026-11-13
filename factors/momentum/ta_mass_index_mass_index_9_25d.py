"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._window_fast=9；self._window_slow=25；self._fillna=False；_run: min_periods = 0 if self._fillna else self._window_slow<br>amplitude = self._high - self._low<br>ema1 = _ema(amplitude, self._window_fast, self._fillna)<br>ema2 = _ema(ema1, self._window_fast, self._fillna)<br>mass = ema1 / ema2<br>self._mass = mass.rolling(self._window_slow, min_periods=min_periods).sum()；mass_index: mass = self._check_fillna(self._mass, value=0)<br>return pd.Series(mass, name=f'mass_index_{self._window_fast}_{self._window_slow}')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：MassIndex.mass_index（window_fast=9, window_slow=25）；追踪：PF00914；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'ta_mass_index_mass_index_9_25d', 'engine': 'ta', 'module': 'trend', 'class': 'MassIndex', 'getter': 'mass_index', 'parameters': {'window_fast': 9, 'window_slow': 25, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_mass_index_mass_index_9_25d', {})
class Factor_ta_mass_index_mass_index_9_25d(PublicFactor):
    name = 'ta_mass_index_mass_index_9_25d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._window_fast=9；self._window_slow=25；self._fillna=False；_run: min_periods = 0 if self._fillna else self._window_slow<br>amplitude = self._high - self._low<br>ema1 = _ema(amplitude, self._window_fast, self._fillna)<br>ema2 = _ema(ema1, self._window_fast, self._fillna)<br>mass = ema1 / ema2<br>self._mass = mass.rolling(self._window_slow, min_periods=min_periods).sum()；mass_index: mass = self._check_fillna(self._mass, value=0)<br>return pd.Series(mass, name=f'mass_index_{self._window_fast}_{self._window_slow}')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：MassIndex.mass_index（window_fast=9, window_slow=25）；追踪：PF00914；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
