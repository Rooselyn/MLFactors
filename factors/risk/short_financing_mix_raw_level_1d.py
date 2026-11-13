"""两融融券成分·原始机制·当日横截面。

公式：B=Q(-div(rqye,rzrqye)); X=B; F=X
类别：风险。业务字段：rqye, rzrqye。
以两融总余额归一融券余额，研究证券借贷供给结构变化，避免直接比较不同规模股票的余额。按当日相对状态研究该机制，较高值表示更偏向所述方向。不把融券份额低认定为必然看多，政策约束会改变份额。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'rqye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rqye'), 'rzrqye': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'rzrqye')}
FORMULA = 'B=Q(-div(rqye,rzrqye)); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('short_financing_mix_raw_level_1d', {})
class Factor_short_financing_mix_raw_level_1d(BaseFactor):
    name = 'short_financing_mix_raw_level_1d'
    description = '以两融总余额归一融券余额，研究证券借贷供给结构变化，避免直接比较不同规模股票的余额。按当日相对状态研究该机制，较高值表示更偏向所述方向。不把融券份额低认定为必然看多，政策约束会改变份额。'
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
            B = cross_section_rank((-divide(values['rqye'], values['rzrqye'])).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
