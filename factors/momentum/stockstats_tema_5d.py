"""Stockstats

公式：完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=5，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_tema(self, meta: _Meta): window = meta.as_int<br>single = self.ema(self[meta.column], window)<br>double = self.ema(single, window)<br>triple = self.ema(double, window)<br>self[meta.name] = 3.0 * single - 3.0 * double + triple；ema(series, window, *, adjust=True, min_periods=1): return series.ewm(ignore_na=False, span=window, min_periods=min_periods, adjust=adjust).mean()；原目录：tema（窗口=5）；追踪：PF01469；[来源](https://github.com/jealous/stockstats)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'),
}
SPEC = {'name': 'stockstats_tema_5d', 'engine': 'stockstats', 'parameters': {'column': 'close_5_tema'}, 'minimum': 1}

@register_factor
@fixed_factor('stockstats_tema_5d', {})
class Factor_stockstats_tema_5d(PublicFactor):
    name = 'stockstats_tema_5d'
    description = '完整数值定义（逐股数组/Series算法，仅返回meta.name对应的主列）：参数meta.window=5，meta.column=close，meta.as_int/int0/int1按固定窗口取值；固定类常量={}；_get_tema(self, meta: _Meta): window = meta.as_int<br>single = self.ema(self[meta.column], window)<br>double = self.ema(single, window)<br>triple = self.ema(double, window)<br>self[meta.name] = 3.0 * single - 3.0 * double + triple；ema(series, window, *, adjust=True, min_periods=1): return series.ewm(ignore_na=False, span=window, min_periods=min_periods, adjust=adjust).mean()；原目录：tema（窗口=5）；追踪：PF01469；[来源](https://github.com/jealous/stockstats)。'
    INPUTS = INPUTS
    SPEC = SPEC
