"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._fillna=False；_run: self._cr = self._close / self._close.iloc[0] - 1<br>self._cr *= 100；cumulative_return: cum_ret = self._check_fillna(self._cr, value=-1)<br>return pd.Series(cum_ret, name='cum_ret')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：CumulativeReturnIndicator.cumulative_return（）；追踪：PF00938；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_cumulative_return_indicator_cumulative_return_alld', 'engine': 'ta', 'module': 'others', 'class': 'CumulativeReturnIndicator', 'getter': 'cumulative_return', 'parameters': {'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_cumulative_return_indicator_cumulative_return_alld', {})
class Factor_ta_cumulative_return_indicator_cumulative_return_alld(PublicFactor):
    name = 'ta_cumulative_return_indicator_cumulative_return_alld'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._fillna=False；_run: self._cr = self._close / self._close.iloc[0] - 1<br>self._cr *= 100；cumulative_return: cum_ret = self._check_fillna(self._cr, value=-1)<br>return pd.Series(cum_ret, name='cum_ret')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：CumulativeReturnIndicator.cumulative_return（）；追踪：PF00938；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
