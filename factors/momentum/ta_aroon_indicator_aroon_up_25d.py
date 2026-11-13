"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._window=25；self._fillna=False；_run: min_periods = 1 if self._fillna else self._window + 1<br>rolling_high = self._high.rolling(self._window + 1, min_periods=min_periods)<br>self._aroon_up = rolling_high.apply(lambda x: float(np.argmax(x)) / self._window * 100, raw=True)<br>rolling_low = self._low.rolling(self._window + 1, min_periods=min_periods)<br>self._aroon_down = rolling_low.apply(lambda x: float(np.argmin(x)) / self._window * 100, raw=True)；aroon_up: aroon_up_series = self._check_fillna(self._aroon_up, value=0)<br>return pd.Series(aroon_up_series, name=f'aroon_up_{self._window}')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：AroonIndicator.aroon_up（window=25）；追踪：PF00904；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'ta_aroon_indicator_aroon_up_25d', 'engine': 'ta', 'module': 'trend', 'class': 'AroonIndicator', 'getter': 'aroon_up', 'parameters': {'window': 25, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_aroon_indicator_aroon_up_25d', {})
class Factor_ta_aroon_indicator_aroon_up_25d(PublicFactor):
    name = 'ta_aroon_indicator_aroon_up_25d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._window=25；self._fillna=False；_run: min_periods = 1 if self._fillna else self._window + 1<br>rolling_high = self._high.rolling(self._window + 1, min_periods=min_periods)<br>self._aroon_up = rolling_high.apply(lambda x: float(np.argmax(x)) / self._window * 100, raw=True)<br>rolling_low = self._low.rolling(self._window + 1, min_periods=min_periods)<br>self._aroon_down = rolling_low.apply(lambda x: float(np.argmin(x)) / self._window * 100, raw=True)；aroon_up: aroon_up_series = self._check_fillna(self._aroon_up, value=0)<br>return pd.Series(aroon_up_series, name=f'aroon_up_{self._window}')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：AroonIndicator.aroon_up（window=25）；追踪：PF00904；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
