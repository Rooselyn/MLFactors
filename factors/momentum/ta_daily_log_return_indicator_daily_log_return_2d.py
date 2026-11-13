"""Python ta（bukosabino）

公式：完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._fillna=False；_run: self._dr = pd.Series(np.log(self._close)).diff()<br>self._dr *= 100；daily_log_return: dr_series = self._check_fillna(self._dr, value=0)<br>return pd.Series(dr_series, name='d_logret')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：DailyLogReturnIndicator.daily_log_return（）；追踪：PF00937；[来源](https://github.com/bukosabino/ta)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'ta_daily_log_return_indicator_daily_log_return_2d', 'engine': 'ta', 'module': 'others', 'class': 'DailyLogReturnIndicator', 'getter': 'daily_log_return', 'parameters': {'fillna': False}, 'minimum': 1}

@register_factor
@fixed_factor('ta_daily_log_return_indicator_daily_log_return_2d', {})
class Factor_ta_daily_log_return_indicator_daily_log_return_2d(PublicFactor):
    name = 'ta_daily_log_return_indicator_daily_log_return_2d'
    description = "完整数值定义（Python算式/递推；self缓存改为局部变量即可）：self._close=C；self._fillna=False；_run: self._dr = pd.Series(np.log(self._close)).diff()<br>self._dr *= 100；daily_log_return: dr_series = self._check_fillna(self._dr, value=0)<br>return pd.Series(dr_series, name='d_logret')；self._check_fillna(x,...)在fillna=False时等于x，不执行任何补齐。；原目录：DailyLogReturnIndicator.daily_log_return（）；追踪：PF00937；[来源](https://github.com/bukosabino/ta)。"
    INPUTS = INPUTS
    SPEC = SPEC
