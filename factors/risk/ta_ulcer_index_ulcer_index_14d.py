"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=14；self._fillna=False；_run: _ui_max = self._close.rolling(self._window, min_periods=1).max()<br>_r_i = 100 * (self._close - _ui_max) / _ui_max<br>def ui_function():<br><br>    def _ui_function(x):<br>        return np.sqrt((x ** 2 / self._window).sum())<br>    return _ui_function<br>self._ulcer_idx = _r_i.rolling(self._window).apply(ui_function(), raw=True)；ulcer_index: ulcer_idx = self._check_fillna(self._ulcer_idx)<br>return pd.Series(ulcer_idx, name='ui')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：UlcerIndex.ulcer_index（window=14）；追踪：PF00903；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_ulcer_index_ulcer_index_14d', 'engine': 'ta', 'module': 'volatility', 'class': 'UlcerIndex', 'getter': 'ulcer_index', 'parameters': {'window': 14, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_ulcer_index_ulcer_index_14d', {})
class Factor_ta_ulcer_index_ulcer_index_14d(PublicFactor):
    name = 'ta_ulcer_index_ulcer_index_14d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=14；self._fillna=False；_run: _ui_max = self._close.rolling(self._window, min_periods=1).max()<br>_r_i = 100 * (self._close - _ui_max) / _ui_max<br>def ui_function():<br><br>    def _ui_function(x):<br>        return np.sqrt((x ** 2 / self._window).sum())<br>    return _ui_function<br>self._ulcer_idx = _r_i.rolling(self._window).apply(ui_function(), raw=True)；ulcer_index: ulcer_idx = self._check_fillna(self._ulcer_idx)<br>return pd.Series(ulcer_idx, name='ui')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：UlcerIndex.ulcer_index（window=14）；追踪：PF00903；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
