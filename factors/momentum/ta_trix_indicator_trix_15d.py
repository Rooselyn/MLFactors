"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=15；self._fillna=False；_run: ema1 = _ema(self._close, self._window, self._fillna)<br>ema2 = _ema(ema1, self._window, self._fillna)<br>ema3 = _ema(ema2, self._window, self._fillna)<br>self._trix = (ema3 - ema3.shift(1, fill_value=ema3.mean())) / ema3.shift(1, fill_value=ema3.mean())<br>self._trix *= 100；trix: trix_series = self._check_fillna(self._trix, value=0)<br>return pd.Series(trix_series, name=f'trix_{self._window}')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：TRIXIndicator.trix（window=15）；追踪：PF00913；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_trix_indicator_trix_15d', 'engine': 'ta', 'module': 'trend', 'class': 'TRIXIndicator', 'getter': 'trix', 'parameters': {'window': 15, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_trix_indicator_trix_15d', {})
class Factor_ta_trix_indicator_trix_15d(PublicFactor):
    name = 'ta_trix_indicator_trix_15d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=15；self._fillna=False；_run: ema1 = _ema(self._close, self._window, self._fillna)<br>ema2 = _ema(ema1, self._window, self._fillna)<br>ema3 = _ema(ema2, self._window, self._fillna)<br>self._trix = (ema3 - ema3.shift(1, fill_value=ema3.mean())) / ema3.shift(1, fill_value=ema3.mean())<br>self._trix *= 100；trix: trix_series = self._check_fillna(self._trix, value=0)<br>return pd.Series(trix_series, name=f'trix_{self._window}')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：TRIXIndicator.trix（window=15）；追踪：PF00913；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
