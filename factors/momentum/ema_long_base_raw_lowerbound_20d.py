"""长周期指数底座·原始机制·保守持续强度。

公式：B=Q(log(div(ema_bfq_90,ema_bfq_250))); X=B; F=Q(M20(X)-SD20(X))
类别：动量。业务字段：ema_bfq_250, ema_bfq_90。
长周期成本高于年线成本时，研究长期价格接受度是否已发生抬升。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'ema_bfq_250': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ema_bfq_250'), 'ema_bfq_90': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'ema_bfq_90')}
FORMULA = 'B=Q(log(div(ema_bfq_90,ema_bfq_250))); X=B; F=Q(M20(X)-SD20(X))'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('ema_long_base_raw_lowerbound_20d', {})
class Factor_ema_long_base_raw_lowerbound_20d(BaseFactor):
    name = 'ema_long_base_raw_lowerbound_20d'
    description = '长周期成本高于年线成本时，研究长期价格接受度是否已发生抬升。按近20日平均状态减去波动衡量保守强度，降低一次尖峰或不稳定信号造成的乐观判断。'
    INPUTS = INPUTS
    FORMULA = FORMULA
    warmup_days = 100
    BOUNDED_HISTORY = True

    def generate_signals(self, data, constituents=None):
        dates = pd.DatetimeIndex(data.index.get_level_values('date').unique()).sort_values()
        symbols = data.index.get_level_values('symbol').unique().sort_values()
        if data.empty:
            return pd.DataFrame(index=dates, columns=symbols, dtype=float)
        eligible = eligibility(data, dates, symbols)
        values = {field: pd.to_numeric(data[field], errors='coerce').unstack('symbol').reindex(index=dates, columns=symbols).astype(float).replace([np.inf, -np.inf], np.nan) for field in self.INPUTS}
        with np.errstate(all='ignore'):
            B = cross_section_rank(np.log(divide(values['ema_bfq_90'], values['ema_bfq_250']).where(divide(values['ema_bfq_90'], values['ema_bfq_250']) > 0)).where(eligible))
            X = B
            F = cross_section_rank((X.rolling(20, min_periods=1).mean() - X.rolling(20, min_periods=1).std(ddof=0)).where(eligible))
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
