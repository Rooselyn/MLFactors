"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._volume=V；self._fillna=False；_run: obv = np.where(self._close < self._close.shift(1), -self._volume, self._volume)<br>self._obv = pd.Series(obv, index=self._close.index).cumsum()；on_balance_volume: obv = self._check_fillna(self._obv, value=0)<br>return pd.Series(obv, name='obv')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：OnBalanceVolumeIndicator.on_balance_volume（）；追踪：PF00940；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ta_on_balance_volume_indicator_on_balance_volume_alld', 'engine': 'ta', 'module': 'volume', 'class': 'OnBalanceVolumeIndicator', 'getter': 'on_balance_volume', 'parameters': {'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_on_balance_volume_indicator_on_balance_volume_alld', {})
class Factor_ta_on_balance_volume_indicator_on_balance_volume_alld(PublicFactor):
    name = 'ta_on_balance_volume_indicator_on_balance_volume_alld'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._volume=V；self._fillna=False；_run: obv = np.where(self._close < self._close.shift(1), -self._volume, self._volume)<br>self._obv = pd.Series(obv, index=self._close.index).cumsum()；on_balance_volume: obv = self._check_fillna(self._obv, value=0)<br>return pd.Series(obv, name='obv')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：OnBalanceVolumeIndicator.on_balance_volume（）；追踪：PF00940；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
