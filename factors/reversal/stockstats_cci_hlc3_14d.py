"""Stockstats

公式：完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=14，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_cci(self, meta: _Meta): window = meta.as_int<br>tp = self._tp()<br>tp_sma = self.sma(tp, window)<br>mad = self._mad(tp, window)<br>divisor = 0.015 * mad<br>self[meta.name] = np.where(divisor != 0, (tp - tp_sma) / divisor, 0.0)；_tp(self): TP=(H+L+C)/3；此处显式选择原源码amount列不存在的分支，不将实际VWAP混入HLC3定义。；sma(cls, series, size): return cls._rolling(series, size).mean()；_mad(cls, series, window): arr = series.values<br>n = len(arr)<br>if window > n:<br>    nan_arr = np.full(n, np.nan)<br>    return pd.Series(nan_arr, index=series.index, name=series.name)<br>sw = np.lib.stride_tricks.sliding_window_view(arr, window)<br>means = sw.mean(axis=1)<br>mad_vals = np.mean(np.abs(sw - means[:, None]), axis=1)<br>out = np.zeros(n, dtype=float)<br>out[window - 1:] = mad_vals<br>return pd.Series(out, index=series.index, name=series.name)；_rolling(series: pd.Series, window: int): return series.rolling(window, min_periods=1, center=False)；原目录：cci（窗口=14）；追踪：PF01492；[来源](https://github.com/jealous/stockstats)。
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
SPEC = {'name': 'stockstats_cci_hlc3_14d', 'engine': 'stockstats', 'parameters': {'column': 'cci'}, 'minimum': 1}

@register_factor
@fixed_factor('stockstats_cci_hlc3_14d', {})
class Factor_stockstats_cci_hlc3_14d(PublicFactor):
    name = 'stockstats_cci_hlc3_14d'
    description = '完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=14，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_cci(self, meta: _Meta): window = meta.as_int<br>tp = self._tp()<br>tp_sma = self.sma(tp, window)<br>mad = self._mad(tp, window)<br>divisor = 0.015 * mad<br>self[meta.name] = np.where(divisor != 0, (tp - tp_sma) / divisor, 0.0)；_tp(self): TP=(H+L+C)/3；此处显式选择原源码amount列不存在的分支，不将实际VWAP混入HLC3定义。；sma(cls, series, size): return cls._rolling(series, size).mean()；_mad(cls, series, window): arr = series.values<br>n = len(arr)<br>if window > n:<br>    nan_arr = np.full(n, np.nan)<br>    return pd.Series(nan_arr, index=series.index, name=series.name)<br>sw = np.lib.stride_tricks.sliding_window_view(arr, window)<br>means = sw.mean(axis=1)<br>mad_vals = np.mean(np.abs(sw - means[:, None]), axis=1)<br>out = np.zeros(n, dtype=float)<br>out[window - 1:] = mad_vals<br>return pd.Series(out, index=series.index, name=series.name)；_rolling(series: pd.Series, window: int): return series.rolling(window, min_periods=1, center=False)；原目录：cci（窗口=14）；追踪：PF01492；[来源](https://github.com/jealous/stockstats)。'
    INPUTS = INPUTS
    SPEC = SPEC
