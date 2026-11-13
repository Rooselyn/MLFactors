"""Stockstats

公式：完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=14，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_atr(self, meta: _Meta): window = meta.as_int<br>self[meta.name] = self._atr(window)；_atr(self, window): tr = self._tr()<br>return self.smma(tr, window)；_tr(self): prev_close = self._shift_arr(self.close.values, -1)<br>high = self.high.values<br>low = self.low.values<br>c1 = high - low<br>c2 = np.abs(high - prev_close)<br>c3 = np.abs(low - prev_close)<br>tr = np.maximum(c1, np.maximum(c2, c3))<br>np.nan_to_num(tr, copy=False)<br>return self.to_series(tr)；smma(series, window): return series.ewm(ignore_na=False, alpha=1.0 / window, min_periods=0, adjust=True).mean()；_shift_arr(arr: np.ndarray, window: int): out = np.empty_like(arr)<br>if window < 0:<br>    k = -window<br>    out[:k] = arr[0]<br>    out[k:] = arr[:-k]<br>else:<br>    k = window<br>    out[:-k] = arr[k:]<br>    out[-k:] = arr[-1]<br>return out；to_series(self, arr: Union[list, np.ndarray]): return pd.Series(arr, index=self.close.index).fillna(0)；原目录：atr（窗口=14）；追踪：PF01491；[来源](https://github.com/jealous/stockstats)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'stockstats_atr_14d', 'engine': 'stockstats', 'parameters': {'column': 'atr'}, 'minimum': 1}

@register_factor
@fixed_factor('stockstats_atr_14d', {})
class Factor_stockstats_atr_14d(PublicFactor):
    name = 'stockstats_atr_14d'
    description = '完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=14，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_atr(self, meta: _Meta): window = meta.as_int<br>self[meta.name] = self._atr(window)；_atr(self, window): tr = self._tr()<br>return self.smma(tr, window)；_tr(self): prev_close = self._shift_arr(self.close.values, -1)<br>high = self.high.values<br>low = self.low.values<br>c1 = high - low<br>c2 = np.abs(high - prev_close)<br>c3 = np.abs(low - prev_close)<br>tr = np.maximum(c1, np.maximum(c2, c3))<br>np.nan_to_num(tr, copy=False)<br>return self.to_series(tr)；smma(series, window): return series.ewm(ignore_na=False, alpha=1.0 / window, min_periods=0, adjust=True).mean()；_shift_arr(arr: np.ndarray, window: int): out = np.empty_like(arr)<br>if window < 0:<br>    k = -window<br>    out[:k] = arr[0]<br>    out[k:] = arr[:-k]<br>else:<br>    k = window<br>    out[:-k] = arr[k:]<br>    out[-k:] = arr[-1]<br>return out；to_series(self, arr: Union[list, np.ndarray]): return pd.Series(arr, index=self.close.index).fillna(0)；原目录：atr（窗口=14）；追踪：PF01491；[来源](https://github.com/jealous/stockstats)。'
    INPUTS = INPUTS
    SPEC = SPEC
