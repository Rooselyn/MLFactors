"""上层成本靠近历史高锚·原始机制·当日横截面。

公式：B=Q(div(cost_95pct,his_high)); X=B; F=X
类别：动量。业务字段：cost_95pct, his_high。
上层成本接近历史高价锚，意味着近期换手成本向高位聚集，研究价格发现能否沿高位成本区延续。按当日相对状态研究该机制，较高值表示更偏向所述方向。历史高锚不是全日最高价，信号也不是标准突破收益率。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'cost_95pct': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'cost_95pct'), 'his_high': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'his_high')}
FORMULA = 'B=Q(div(cost_95pct,his_high)); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('chip_high_anchor_raw_level_1d', {})
class Factor_chip_high_anchor_raw_level_1d(BaseFactor):
    name = 'chip_high_anchor_raw_level_1d'
    description = '上层成本接近历史高价锚，意味着近期换手成本向高位聚集，研究价格发现能否沿高位成本区延续。按当日相对状态研究该机制，较高值表示更偏向所述方向。历史高锚不是全日最高价，信号也不是标准突破收益率。'
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
            B = cross_section_rank(divide(values['cost_95pct'], values['his_high']).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
