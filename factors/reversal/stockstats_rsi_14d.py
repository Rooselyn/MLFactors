"""Stockstats

公式：完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=14，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_rsi(self, meta: _Meta): self[meta.name] = self._rsi(meta.as_int)；_rsi(self, window): close = self.close.values<br>diff = self._np_diff(close)<br>up = np.where(diff > 0, diff, 0.0)<br>down = np.where(diff < 0, -diff, 0.0)<br>up_sma = self.smma(pd.Series(up), window).values<br>down_sma = self.smma(pd.Series(down), window).values<br>total_chg = up_sma + down_sma<br>with np.errstate(divide='ignore', invalid='ignore'):<br>    rsi = np.where(total_chg != 0, 100 * (up_sma / total_chg), 50.0)<br>rsi[0] = 50.0<br>return self.to_series(rsi)；_np_diff(arr: np.ndarray): diff = np.zeros_like(arr)<br>diff[1:] = np.diff(arr)<br>return diff；to_series(self, arr: Union[list, np.ndarray]): return pd.Series(arr, index=self.close.index).fillna(0)；smma(series, window): return series.ewm(ignore_na=False, alpha=1.0 / window, min_periods=0, adjust=True).mean()；原目录：rsi（窗口=14）；追踪：PF01474；[来源](https://github.com/jealous/stockstats)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'stockstats_rsi_14d', 'engine': 'stockstats', 'parameters': {'column': 'close_14_rsi'}, 'minimum': 1}

@register_factor
@fixed_factor('stockstats_rsi_14d', {})
class Factor_stockstats_rsi_14d(PublicFactor):
    name = 'stockstats_rsi_14d'
    description = "完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=14，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_rsi(self, meta: _Meta): self[meta.name] = self._rsi(meta.as_int)；_rsi(self, window): close = self.close.values<br>diff = self._np_diff(close)<br>up = np.where(diff > 0, diff, 0.0)<br>down = np.where(diff < 0, -diff, 0.0)<br>up_sma = self.smma(pd.Series(up), window).values<br>down_sma = self.smma(pd.Series(down), window).values<br>total_chg = up_sma + down_sma<br>with np.errstate(divide='ignore', invalid='ignore'):<br>    rsi = np.where(total_chg != 0, 100 * (up_sma / total_chg), 50.0)<br>rsi[0] = 50.0<br>return self.to_series(rsi)；_np_diff(arr: np.ndarray): diff = np.zeros_like(arr)<br>diff[1:] = np.diff(arr)<br>return diff；to_series(self, arr: Union[list, np.ndarray]): return pd.Series(arr, index=self.close.index).fillna(0)；smma(series, window): return series.ewm(ignore_na=False, alpha=1.0 / window, min_periods=0, adjust=True).mean()；原目录：rsi（窗口=14）；追踪：PF01474；[来源](https://github.com/jealous/stockstats)。"
    INPUTS = INPUTS
    SPEC = SPEC
