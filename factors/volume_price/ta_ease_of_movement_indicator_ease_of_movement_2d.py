"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._volume=V；self._window=14；self._fillna=False；_run: self._emv = (self._high.diff(1) + self._low.diff(1)) * (self._high - self._low) / (2 * self._volume)<br>self._emv *= 100000000；ease_of_movement: emv = self._check_fillna(self._emv, value=0)<br>return pd.Series(emv, name=f'eom_{self._window}')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：EaseOfMovementIndicator.ease_of_movement（window=14）；追踪：PF00942；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ta_ease_of_movement_indicator_ease_of_movement_2d', 'engine': 'ta', 'module': 'volume', 'class': 'EaseOfMovementIndicator', 'getter': 'ease_of_movement', 'parameters': {'window': 14, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_ease_of_movement_indicator_ease_of_movement_2d', {})
class Factor_ta_ease_of_movement_indicator_ease_of_movement_2d(PublicFactor):
    name = 'ta_ease_of_movement_indicator_ease_of_movement_2d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._volume=V；self._window=14；self._fillna=False；_run: self._emv = (self._high.diff(1) + self._low.diff(1)) * (self._high - self._low) / (2 * self._volume)<br>self._emv *= 100000000；ease_of_movement: emv = self._check_fillna(self._emv, value=0)<br>return pd.Series(emv, name=f'eom_{self._window}')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：EaseOfMovementIndicator.ease_of_movement（window=14）；追踪：PF00942；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
