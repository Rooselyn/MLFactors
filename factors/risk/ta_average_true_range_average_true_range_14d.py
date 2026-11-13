"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._close=C；self._window=14；self._fillna=False；_run: close_shift = self._close.shift(1)<br>true_range = self._true_range(self._high, self._low, close_shift)<br>atr = np.zeros(len(self._close))<br>atr[self._window - 1] = true_range[0:self._window].mean()<br>for i in range(self._window, len(atr)):<br>    atr[i] = (atr[i - 1] * (self._window - 1) + true_range.iloc[i]) / float(self._window)<br>self._atr = pd.Series(data=atr, index=true_range.index)；average_true_range: atr = self._check_fillna(self._atr, value=0)<br>return pd.Series(atr, name='atr')；辅助算子 _true_range(high: pd.Series, low: pd.Series, prev_close: pd.Series): tr1 = high - low<br>tr2 = (high - prev_close).abs()<br>tr3 = (low - prev_close).abs()<br>true_range = pd.DataFrame(data={'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)<br>return true_range；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：AverageTrueRange.average_true_range（window=14）；追踪：PF00887；[来源](https://github.com/bukosabino/ta)。
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
SPEC = {'name': 'ta_average_true_range_average_true_range_14d', 'engine': 'ta', 'module': 'volatility', 'class': 'AverageTrueRange', 'getter': 'average_true_range', 'parameters': {'window': 14, 'fillna': False}, 'minimum': 14}

@register_factor
@fixed_factor('ta_average_true_range_average_true_range_14d', {})
class Factor_ta_average_true_range_average_true_range_14d(PublicFactor):
    name = 'ta_average_true_range_average_true_range_14d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._close=C；self._window=14；self._fillna=False；_run: close_shift = self._close.shift(1)<br>true_range = self._true_range(self._high, self._low, close_shift)<br>atr = np.zeros(len(self._close))<br>atr[self._window - 1] = true_range[0:self._window].mean()<br>for i in range(self._window, len(atr)):<br>    atr[i] = (atr[i - 1] * (self._window - 1) + true_range.iloc[i]) / float(self._window)<br>self._atr = pd.Series(data=atr, index=true_range.index)；average_true_range: atr = self._check_fillna(self._atr, value=0)<br>return pd.Series(atr, name='atr')；辅助算子 _true_range(high: pd.Series, low: pd.Series, prev_close: pd.Series): tr1 = high - low<br>tr2 = (high - prev_close).abs()<br>tr3 = (low - prev_close).abs()<br>true_range = pd.DataFrame(data={'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)<br>return true_range；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：AverageTrueRange.average_true_range（window=14）；追踪：PF00887；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
