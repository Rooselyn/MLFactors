"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._close=C；self._volume=V；self._fillna=False；_run: clv = (self._close - self._low - (self._high - self._close)) / (self._high - self._low)<br>clv = clv.fillna(0.0)<br>adi = clv * self._volume<br>self._adi = adi.cumsum()；acc_dist_index: adi = self._check_fillna(self._adi, value=0)<br>return pd.Series(adi, name='adi')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：AccDistIndexIndicator.acc_dist_index（）；追踪：PF00939；[来源](https://github.com/bukosabino/ta)。
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
SPEC = {'name': 'ta_acc_dist_index_indicator_acc_dist_index_alld', 'engine': 'ta', 'module': 'volume', 'class': 'AccDistIndexIndicator', 'getter': 'acc_dist_index', 'parameters': {'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_acc_dist_index_indicator_acc_dist_index_alld', {})
class Factor_ta_acc_dist_index_indicator_acc_dist_index_alld(PublicFactor):
    name = 'ta_acc_dist_index_indicator_acc_dist_index_alld'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._high=H；self._low=L；self._close=C；self._volume=V；self._fillna=False；_run: clv = (self._close - self._low - (self._high - self._close)) / (self._high - self._low)<br>clv = clv.fillna(0.0)<br>adi = clv * self._volume<br>self._adi = adi.cumsum()；acc_dist_index: adi = self._check_fillna(self._adi, value=0)<br>return pd.Series(adi, name='adi')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：AccDistIndexIndicator.acc_dist_index（）；追踪：PF00939；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
