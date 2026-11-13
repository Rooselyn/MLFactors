"""新高新低回溯优势·原始机制·当日横截面。

公式：B=Q(log1p(topdays)-log1p(lowdays)); X=B; F=X
类别：动量。业务字段：lowdays, topdays。
比较新高与新低对应的回溯跨度，研究突破影响是否覆盖更长历史成本区间。按当日相对状态研究该机制，较高值表示更偏向所述方向。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'lowdays': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'lowdays'), 'topdays': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'topdays')}
FORMULA = 'B=Q(log1p(topdays)-log1p(lowdays)); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

@register_factor
@fixed_factor('record_horizon_raw_level_1d', {})
class Factor_record_horizon_raw_level_1d(BaseFactor):
    name = 'record_horizon_raw_level_1d'
    description = '比较新高与新低对应的回溯跨度，研究突破影响是否覆盖更长历史成本区间。按当日相对状态研究该机制，较高值表示更偏向所述方向。'
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
            B = cross_section_rank((np.log1p(values['topdays'].where(values['topdays'] > -1)) - np.log1p(values['lowdays'].where(values['lowdays'] > -1))).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
