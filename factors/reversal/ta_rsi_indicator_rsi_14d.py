"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=14；self._fillna=False；_run: diff = self._close.diff(1)<br>up_direction = diff.where(diff > 0, 0.0)<br>down_direction = -diff.where(diff < 0, 0.0)<br>min_periods = 0 if self._fillna else self._window<br>emaup = up_direction.ewm(alpha=1 / self._window, min_periods=min_periods, adjust=False).mean()<br>emadn = down_direction.ewm(alpha=1 / self._window, min_periods=min_periods, adjust=False).mean()<br>relative_strength = emaup / emadn<br>self._rsi = pd.Series(np.where(emadn == 0, 100, 100 - 100 / (1 + relative_strength)), index=self._close.index)；rsi: rsi_series = self._check_fillna(self._rsi, value=50)<br>return pd.Series(rsi_series, name='rsi')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：RSIIndicator.rsi（window=14）；追踪：PF00947；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_rsi_indicator_rsi_14d', 'engine': 'ta', 'module': 'momentum', 'class': 'RSIIndicator', 'getter': 'rsi', 'parameters': {'window': 14, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_rsi_indicator_rsi_14d', {})
class Factor_ta_rsi_indicator_rsi_14d(PublicFactor):
    name = 'ta_rsi_indicator_rsi_14d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=14；self._fillna=False；_run: diff = self._close.diff(1)<br>up_direction = diff.where(diff > 0, 0.0)<br>down_direction = -diff.where(diff < 0, 0.0)<br>min_periods = 0 if self._fillna else self._window<br>emaup = up_direction.ewm(alpha=1 / self._window, min_periods=min_periods, adjust=False).mean()<br>emadn = down_direction.ewm(alpha=1 / self._window, min_periods=min_periods, adjust=False).mean()<br>relative_strength = emaup / emadn<br>self._rsi = pd.Series(np.where(emadn == 0, 100, 100 - 100 / (1 + relative_strength)), index=self._close.index)；rsi: rsi_series = self._check_fillna(self._rsi, value=50)<br>return pd.Series(rsi_series, name='rsi')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：RSIIndicator.rsi（window=14）；追踪：PF00947；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
