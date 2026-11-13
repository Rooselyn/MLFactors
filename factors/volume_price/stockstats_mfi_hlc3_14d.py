"""Stockstats

公式：完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=14，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_mfi(self, meta: _Meta): window = meta.as_int<br>tp = self._tp().values<br>volume = self.volume.values<br>raw_money_flow = tp * volume<br>tp_diff = np.zeros_like(tp)<br>tp_diff[1:] = np.diff(tp)<br>pos_flow = np.where(tp_diff > 0, raw_money_flow, 0.0)<br>neg_flow = np.where(tp_diff < 0, raw_money_flow, 0.0)<br>pos_sum = self._rolling_sum(pos_flow, window)<br>neg_sum = self._rolling_sum(neg_flow, window)<br>total_flow = pos_sum + neg_sum<br>mfi = np.divide(pos_sum, total_flow, out=np.full_like(pos_sum, 0.5), where=total_flow > 0)<br>mfi[:window] = 0.5<br>self[meta.name] = self.to_series(mfi)；_rolling_sum(arr, window): n = len(arr)<br>out = np.zeros(n, dtype=float)<br>cumsum = np.cumsum(arr)<br>out[window:] = cumsum[window:] - cumsum[:-window]<br>out[:window] = cumsum[:window]<br>return out；to_series(self, arr: Union[list, np.ndarray]): return pd.Series(arr, index=self.close.index).fillna(0)；_tp(self): TP=(H+L+C)/3；此处显式选择原源码amount列不存在的分支，不将实际VWAP混入HLC3定义。；原目录：mfi（窗口=14）；追踪：PF01498；[来源](https://github.com/jealous/stockstats)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
    'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'),
    'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'),
    'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'),
}
SPEC = {'name': 'stockstats_mfi_hlc3_14d', 'engine': 'stockstats', 'parameters': {'column': 'mfi'}, 'minimum': 1}

@register_factor
@fixed_factor('stockstats_mfi_hlc3_14d', {})
class Factor_stockstats_mfi_hlc3_14d(PublicFactor):
    name = 'stockstats_mfi_hlc3_14d'
    description = '完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=14，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_mfi(self, meta: _Meta): window = meta.as_int<br>tp = self._tp().values<br>volume = self.volume.values<br>raw_money_flow = tp * volume<br>tp_diff = np.zeros_like(tp)<br>tp_diff[1:] = np.diff(tp)<br>pos_flow = np.where(tp_diff > 0, raw_money_flow, 0.0)<br>neg_flow = np.where(tp_diff < 0, raw_money_flow, 0.0)<br>pos_sum = self._rolling_sum(pos_flow, window)<br>neg_sum = self._rolling_sum(neg_flow, window)<br>total_flow = pos_sum + neg_sum<br>mfi = np.divide(pos_sum, total_flow, out=np.full_like(pos_sum, 0.5), where=total_flow > 0)<br>mfi[:window] = 0.5<br>self[meta.name] = self.to_series(mfi)；_rolling_sum(arr, window): n = len(arr)<br>out = np.zeros(n, dtype=float)<br>cumsum = np.cumsum(arr)<br>out[window:] = cumsum[window:] - cumsum[:-window]<br>out[:window] = cumsum[:window]<br>return out；to_series(self, arr: Union[list, np.ndarray]): return pd.Series(arr, index=self.close.index).fillna(0)；_tp(self): TP=(H+L+C)/3；此处显式选择原源码amount列不存在的分支，不将实际VWAP混入HLC3定义。；原目录：mfi（窗口=14）；追踪：PF01498；[来源](https://github.com/jealous/stockstats)。'
    INPUTS = INPUTS
    SPEC = SPEC
