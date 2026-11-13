"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._close=C；self._volume=V；self._window=14；self._fillna=False；_run: typical_price = (self._high + self._low + self._close) / 3.0<br>typical_price_volume = typical_price * self._volume<br>min_periods = 0 if self._fillna else self._window<br>total_pv = typical_price_volume.rolling(self._window, min_periods=min_periods).sum()<br>total_volume = self._volume.rolling(self._window, min_periods=min_periods).sum()<br>self.vwap = total_pv / total_volume；volume_weighted_average_price: vwap = self._check_fillna(self.vwap)<br>return pd.Series(vwap, name=f'vwap_{self._window}')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：VolumeWeightedAveragePrice.volume_weighted_average_price（window=14）；追踪：PF00946；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ta_volume_weighted_average_price_volume_weighted_average_price_14d', 'engine': 'ta', 'module': 'volume', 'class': 'VolumeWeightedAveragePrice', 'getter': 'volume_weighted_average_price', 'parameters': {'window': 14, 'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_volume_weighted_average_price_volume_weighted_average_price_14d', {})
class Factor_ta_volume_weighted_average_price_volume_weighted_average_price_14d(PublicFactor):
    name = 'ta_volume_weighted_average_price_volume_weighted_average_price_14d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._close=C；self._volume=V；self._window=14；self._fillna=False；_run: typical_price = (self._high + self._low + self._close) / 3.0<br>typical_price_volume = typical_price * self._volume<br>min_periods = 0 if self._fillna else self._window<br>total_pv = typical_price_volume.rolling(self._window, min_periods=min_periods).sum()<br>total_volume = self._volume.rolling(self._window, min_periods=min_periods).sum()<br>self.vwap = total_pv / total_volume；volume_weighted_average_price: vwap = self._check_fillna(self.vwap)<br>return pd.Series(vwap, name=f'vwap_{self._window}')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：VolumeWeightedAveragePrice.volume_weighted_average_price（window=14）；追踪：PF00946；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
