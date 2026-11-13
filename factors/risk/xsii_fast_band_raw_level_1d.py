"""薛斯快带相对宽度·原始机制·当日横截面。

公式：B=Q(-div(abs(xsii_td1_bfq-xsii_td2_bfq),abs(xsii_td1_bfq)+abs(xsii_td2_bfq))); X=B; F=X
类别：风险。业务字段：xsii_td1_bfq, xsii_td2_bfq。
快成本带的相对宽度衡量近端价格分歧，研究交易冲击较低的状态。按当日相对状态研究该机制，较高值表示更偏向所述方向。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'xsii_td1_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'xsii_td1_bfq'), 'xsii_td2_bfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'xsii_td2_bfq')}
FORMULA = 'B=Q(-div(abs(xsii_td1_bfq-xsii_td2_bfq),abs(xsii_td1_bfq)+abs(xsii_td2_bfq))); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

def divide(a, b):
    if isinstance(b, pd.DataFrame):
        return a / b.where(b != 0)
    return a / b if b != 0 else a * np.nan

@register_factor
@fixed_factor('xsii_fast_band_raw_level_1d', {})
class Factor_xsii_fast_band_raw_level_1d(BaseFactor):
    name = 'xsii_fast_band_raw_level_1d'
    description = '快成本带的相对宽度衡量近端价格分歧，研究交易冲击较低的状态。按当日相对状态研究该机制，较高值表示更偏向所述方向。'
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
            B = cross_section_rank((-divide(abs(values['xsii_td1_bfq'] - values['xsii_td2_bfq']), abs(values['xsii_td1_bfq']) + abs(values['xsii_td2_bfq']))).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
