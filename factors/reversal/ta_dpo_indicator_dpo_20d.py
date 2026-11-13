"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=20；self._fillna=False；_run: min_periods = 0 if self._fillna else self._window<br>self._dpo = self._close.shift(int(0.5 * self._window + 1), fill_value=self._close.mean()) - self._close.rolling(self._window, min_periods=min_periods).mean()；dpo: dpo_series = self._check_fillna(self._dpo, value=0)<br>return pd.Series(dpo_series, name='dpo_' + str(self._window))；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：DPOIndicator.dpo（window=20）；追踪：PF00922；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_dpo_indicator_dpo_20d', 'engine': 'ta', 'module': 'trend', 'class': 'DPOIndicator', 'getter': 'dpo', 'parameters': {'window': 20, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_dpo_indicator_dpo_20d', {})
class Factor_ta_dpo_indicator_dpo_20d(PublicFactor):
    name = 'ta_dpo_indicator_dpo_20d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=20；self._fillna=False；_run: min_periods = 0 if self._fillna else self._window<br>self._dpo = self._close.shift(int(0.5 * self._window + 1), fill_value=self._close.mean()) - self._close.rolling(self._window, min_periods=min_periods).mean()；dpo: dpo_series = self._check_fillna(self._dpo, value=0)<br>return pd.Series(dpo_series, name='dpo_' + str(self._window))；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：DPOIndicator.dpo（window=20）；追踪：PF00922；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
