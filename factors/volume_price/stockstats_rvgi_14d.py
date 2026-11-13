"""Stockstats

公式：完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=14，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_rvgi(self, meta: _Meta): rvgi = self._rvgi(meta.as_int).values.copy()<br>rvgi[:3] = 0.0<br>rvgi_s = self._sym_wma4(rvgi)<br>rvgi_s[:6] = 0.0<br>self[meta.name] = self.to_series(rvgi)<br>self[meta.name_ex('s')] = self.to_series(rvgi_s)；_sym_wma4(arr: np.ndarray): weights = np.array([1, 2, 2, 1], dtype=float)<br>weights /= weights.sum()<br>conv = np.convolve(arr, weights, mode='valid')<br>out = np.zeros(len(arr), dtype=float)<br>out[len(weights) - 1:] = conv<br>return out；to_series(self, arr: Union[list, np.ndarray]): return pd.Series(arr, index=self.close.index).fillna(0)；_rvgi(self, window: int): co = self.close.values - self.open.values<br>hl = self.high.values - self.low.values<br>nu = self.to_series(self._sym_wma4(co))<br>de = self.to_series(self._sym_wma4(hl))<br>ret = self.sma(nu, window) / self.sma(de, window)<br>return ret；sma(cls, series, size): return cls._rolling(series, size).mean()；_rolling(series: pd.Series, window: int): return series.rolling(window, min_periods=1, center=False)；原目录：rvgi（窗口=14）；追踪：PF01501；[来源](https://github.com/jealous/stockstats)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
    'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'),
}
SPEC = {'name': 'stockstats_rvgi_14d', 'engine': 'stockstats', 'parameters': {'column': 'rvgi'}, 'minimum': 4}

@register_factor
@fixed_factor('stockstats_rvgi_14d', {})
class Factor_stockstats_rvgi_14d(PublicFactor):
    name = 'stockstats_rvgi_14d'
    description = "完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=14，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_rvgi(self, meta: _Meta): rvgi = self._rvgi(meta.as_int).values.copy()<br>rvgi[:3] = 0.0<br>rvgi_s = self._sym_wma4(rvgi)<br>rvgi_s[:6] = 0.0<br>self[meta.name] = self.to_series(rvgi)<br>self[meta.name_ex('s')] = self.to_series(rvgi_s)；_sym_wma4(arr: np.ndarray): weights = np.array([1, 2, 2, 1], dtype=float)<br>weights /= weights.sum()<br>conv = np.convolve(arr, weights, mode='valid')<br>out = np.zeros(len(arr), dtype=float)<br>out[len(weights) - 1:] = conv<br>return out；to_series(self, arr: Union[list, np.ndarray]): return pd.Series(arr, index=self.close.index).fillna(0)；_rvgi(self, window: int): co = self.close.values - self.open.values<br>hl = self.high.values - self.low.values<br>nu = self.to_series(self._sym_wma4(co))<br>de = self.to_series(self._sym_wma4(hl))<br>ret = self.sma(nu, window) / self.sma(de, window)<br>return ret；sma(cls, series, size): return cls._rolling(series, size).mean()；_rolling(series: pd.Series, window: int): return series.rolling(window, min_periods=1, center=False)；原目录：rvgi（窗口=14）；追踪：PF01501；[来源](https://github.com/jealous/stockstats)。"
    INPUTS = INPUTS
    SPEC = SPEC
