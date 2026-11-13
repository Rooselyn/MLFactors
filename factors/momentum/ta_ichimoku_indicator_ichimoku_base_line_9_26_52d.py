"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._window1=9；self._window2=26；self._window3=52；self._visual=False；self._fillna=False；_run: min_periods_n1 = 0 if self._fillna else self._window1<br>min_periods_n2 = 0 if self._fillna else self._window2<br>self._conv = 0.5 * (self._high.rolling(self._window1, min_periods=min_periods_n1).max() + self._low.rolling(self._window1, min_periods=min_periods_n1).min())<br>self._base = 0.5 * (self._high.rolling(self._window2, min_periods=min_periods_n2).max() + self._low.rolling(self._window2, min_periods=min_periods_n2).min())；ichimoku_base_line: base = self._check_fillna(self._base, value=-1)<br>return pd.Series(base, name=f'ichimoku_base_{self._window1}_{self._window2}')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：IchimokuIndicator.ichimoku_base_line（window1=9, window2=26, window3=52）；追踪：PF00916；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'ta_ichimoku_indicator_ichimoku_base_line_9_26_52d', 'engine': 'ta', 'module': 'trend', 'class': 'IchimokuIndicator', 'getter': 'ichimoku_base_line', 'parameters': {'window1': 9, 'window2': 26, 'window3': 52, 'visual': False, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_ichimoku_indicator_ichimoku_base_line_9_26_52d', {})
class Factor_ta_ichimoku_indicator_ichimoku_base_line_9_26_52d(PublicFactor):
    name = 'ta_ichimoku_indicator_ichimoku_base_line_9_26_52d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._window1=9；self._window2=26；self._window3=52；self._visual=False；self._fillna=False；_run: min_periods_n1 = 0 if self._fillna else self._window1<br>min_periods_n2 = 0 if self._fillna else self._window2<br>self._conv = 0.5 * (self._high.rolling(self._window1, min_periods=min_periods_n1).max() + self._low.rolling(self._window1, min_periods=min_periods_n1).min())<br>self._base = 0.5 * (self._high.rolling(self._window2, min_periods=min_periods_n2).max() + self._low.rolling(self._window2, min_periods=min_periods_n2).min())；ichimoku_base_line: base = self._check_fillna(self._base, value=-1)<br>return pd.Series(base, name=f'ichimoku_base_{self._window1}_{self._window2}')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：IchimokuIndicator.ichimoku_base_line（window1=9, window2=26, window3=52）；追踪：PF00916；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
