"""Stockstats

公式：完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=12，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_trix(self, meta: _Meta): window = meta.as_int<br>single = self.ema(self[meta.column], window)<br>double = self.ema(single, window)<br>triple = self.ema(double, window)<br>triple_values = triple.values<br>trix = np.zeros_like(triple_values)<br>with np.errstate(divide='ignore', invalid='ignore'):<br>    trix[1:] = (triple_values[1:] / triple_values[:-1] - 1) * 100<br>self[meta.name] = self.to_series(trix)；ema(series, window, *, adjust=True, min_periods=1): return series.ewm(ignore_na=False, span=window, min_periods=min_periods, adjust=adjust).mean()；to_series(self, arr: Union[list, np.ndarray]): return pd.Series(arr, index=self.close.index).fillna(0)；原目录：trix（窗口=12）；追踪：PF01488；[来源](https://github.com/jealous/stockstats)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'stockstats_trix_12d', 'engine': 'stockstats', 'parameters': {'column': 'close_12_trix'}, 'minimum': 1}

@register_factor
@fixed_factor('stockstats_trix_12d', {})
class Factor_stockstats_trix_12d(PublicFactor):
    name = 'stockstats_trix_12d'
    description = "完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=12，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_trix(self, meta: _Meta): window = meta.as_int<br>single = self.ema(self[meta.column], window)<br>double = self.ema(single, window)<br>triple = self.ema(double, window)<br>triple_values = triple.values<br>trix = np.zeros_like(triple_values)<br>with np.errstate(divide='ignore', invalid='ignore'):<br>    trix[1:] = (triple_values[1:] / triple_values[:-1] - 1) * 100<br>self[meta.name] = self.to_series(trix)；ema(series, window, *, adjust=True, min_periods=1): return series.ewm(ignore_na=False, span=window, min_periods=min_periods, adjust=adjust).mean()；to_series(self, arr: Union[list, np.ndarray]): return pd.Series(arr, index=self.close.index).fillna(0)；原目录：trix（窗口=12）；追踪：PF01488；[来源](https://github.com/jealous/stockstats)。"
    INPUTS = INPUTS
    SPEC = SPEC
