"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._volume=V；self._fillna=False；self._smoothing_factor=None；self._dropnans=False；_run: self._vpt = (self._close.pct_change() * self._volume).cumsum()<br>if self._smoothing_factor:<br>    min_periods = 0 if self._fillna else self._smoothing_factor<br>    self._vpt = self._vpt.rolling(self._smoothing_factor, min_periods=min_periods).mean()<br>if self._dropnans:<br>    self._vpt = self._vpt.dropna()；volume_price_trend: vpt = self._check_fillna(self._vpt, value=0)<br>return pd.Series(vpt, name='vpt')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：VolumePriceTrendIndicator.volume_price_trend（smoothing_factor=None, dropnans=False）；追踪：PF00944；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ta_volume_price_trend_indicator_volume_price_trend_alld', 'engine': 'ta', 'module': 'volume', 'class': 'VolumePriceTrendIndicator', 'getter': 'volume_price_trend', 'parameters': {'fillna': False, 'smoothing_factor': None, 'dropnans': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_volume_price_trend_indicator_volume_price_trend_alld', {})
class Factor_ta_volume_price_trend_indicator_volume_price_trend_alld(PublicFactor):
    name = 'ta_volume_price_trend_indicator_volume_price_trend_alld'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._volume=V；self._fillna=False；self._smoothing_factor=None；self._dropnans=False；_run: self._vpt = (self._close.pct_change() * self._volume).cumsum()<br>if self._smoothing_factor:<br>    min_periods = 0 if self._fillna else self._smoothing_factor<br>    self._vpt = self._vpt.rolling(self._smoothing_factor, min_periods=min_periods).mean()<br>if self._dropnans:<br>    self._vpt = self._vpt.dropna()；volume_price_trend: vpt = self._check_fillna(self._vpt, value=0)<br>return pd.Series(vpt, name='vpt')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：VolumePriceTrendIndicator.volume_price_trend（smoothing_factor=None, dropnans=False）；追踪：PF00944；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
