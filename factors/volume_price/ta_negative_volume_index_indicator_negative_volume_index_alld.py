"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._volume=V；self._fillna=False；_run: price_change = self._close.pct_change()<br>vol_decrease = self._volume.shift(1) > self._volume<br>self._nvi = pd.Series(data=np.nan, index=self._close.index, dtype='float64', name='nvi')<br>self._nvi.iloc[0] = 1000<br>for i in range(1, len(self._nvi)):<br>    if vol_decrease.iloc[i]:<br>        self._nvi.iloc[i] = self._nvi.iloc[i - 1] * (1.0 + price_change.iloc[i])<br>    else:<br>        self._nvi.iloc[i] = self._nvi.iloc[i - 1]；negative_volume_index: nvi = self._check_fillna(self._nvi, value=1000)<br>return pd.Series(nvi, name='nvi')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：NegativeVolumeIndexIndicator.negative_volume_index（）；追踪：PF00945；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
}
SPEC = {'name': 'ta_negative_volume_index_indicator_negative_volume_index_alld', 'engine': 'ta', 'module': 'volume', 'class': 'NegativeVolumeIndexIndicator', 'getter': 'negative_volume_index', 'parameters': {'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_negative_volume_index_indicator_negative_volume_index_alld', {})
class Factor_ta_negative_volume_index_indicator_negative_volume_index_alld(PublicFactor):
    name = 'ta_negative_volume_index_indicator_negative_volume_index_alld'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._volume=V；self._fillna=False；_run: price_change = self._close.pct_change()<br>vol_decrease = self._volume.shift(1) > self._volume<br>self._nvi = pd.Series(data=np.nan, index=self._close.index, dtype='float64', name='nvi')<br>self._nvi.iloc[0] = 1000<br>for i in range(1, len(self._nvi)):<br>    if vol_decrease.iloc[i]:<br>        self._nvi.iloc[i] = self._nvi.iloc[i - 1] * (1.0 + price_change.iloc[i])<br>    else:<br>        self._nvi.iloc[i] = self._nvi.iloc[i - 1]；negative_volume_index: nvi = self._check_fillna(self._nvi, value=1000)<br>return pd.Series(nvi, name='nvi')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：NegativeVolumeIndexIndicator.negative_volume_index（）；追踪：PF00945；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
