"""开盘自由流通市值·原始机制·当日横截面。

公式：B=Q(-log(10000*free_share*open)); X=B; F=X
类别：规模。业务字段：free_share, open。
以自由流通股本乘开盘价衡量可交易市值，研究A股交易供给较小股票的规模溢价及其容量约束。按当日相对状态研究该机制，较高值表示更偏向所述方向。这是开盘口径自由流通市值，不冒充收盘总市值。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'free_share': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'free_share'), 'open': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open')}
FORMULA = 'B=Q(-log(10000*free_share*open)); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

@register_factor
@fixed_factor('free_cap_raw_level_1d', {})
class Factor_free_cap_raw_level_1d(BaseFactor):
    name = 'free_cap_raw_level_1d'
    description = '以自由流通股本乘开盘价衡量可交易市值，研究A股交易供给较小股票的规模溢价及其容量约束。按当日相对状态研究该机制，较高值表示更偏向所述方向。这是开盘口径自由流通市值，不冒充收盘总市值。'
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
            B = cross_section_rank((-np.log((10000 * values['free_share'] * values['open']).where(10000 * values['free_share'] * values['open'] > 0))).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
