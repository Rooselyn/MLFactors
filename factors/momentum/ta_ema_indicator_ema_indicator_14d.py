"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=14；self._fillna=False；ema_indicator: ema_ = _ema(self._close, self._window, self._fillna)<br>return pd.Series(ema_, name=f'ema_{self._window}')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：EMAIndicator.ema_indicator（window=14）；追踪：PF00910；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_ema_indicator_ema_indicator_14d', 'engine': 'ta', 'module': 'trend', 'class': 'EMAIndicator', 'getter': 'ema_indicator', 'parameters': {'window': 14, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_ema_indicator_ema_indicator_14d', {})
class Factor_ta_ema_indicator_ema_indicator_14d(PublicFactor):
    name = 'ta_ema_indicator_ema_indicator_14d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._window=14；self._fillna=False；ema_indicator: ema_ = _ema(self._close, self._window, self._fillna)<br>return pd.Series(ema_, name=f'ema_{self._window}')；辅助算子 _ema(series, periods: int, fillna: bool=False): min_periods = 0 if fillna else periods<br>return series.ewm(span=periods, min_periods=min_periods, adjust=False).mean()；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：EMAIndicator.ema_indicator（window=14）；追踪：PF00910；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
