"""随机指标短线过冲·原始机制·当日横截面。

公式：B=Q(-(kdj_k_hfq-kdj_d_hfq)/100); X=B; F=X
类别：反转。业务字段：kdj_d_hfq, kdj_k_hfq。
快随机指标相对慢随机指标跃升过多，研究短线情绪领先平滑状态后的回归。按当日相对状态研究该机制，较高值表示更偏向所述方向。
计算算子与固定公式均在本文件实现；滚动约定见自研单因子-日线.md。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
from factors.base import eligibility
import pandas as pd
INPUTS = {'kdj_d_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'kdj_d_hfq'), 'kdj_k_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'kdj_k_hfq')}
FORMULA = 'B=Q(-(kdj_k_hfq-kdj_d_hfq)/100); X=B; F=X'

def cross_section_rank(value):
    value = value.replace([np.inf, -np.inf], np.nan)
    count = value.count(axis=1).replace(0, np.nan)
    return 2 * value.rank(axis=1, method='average').sub(0.5).div(count, axis=0) - 1

@register_factor
@fixed_factor('kdj_fast_slow_raw_level_1d', {})
class Factor_kdj_fast_slow_raw_level_1d(BaseFactor):
    name = 'kdj_fast_slow_raw_level_1d'
    description = '快随机指标相对慢随机指标跃升过多，研究短线情绪领先平滑状态后的回归。按当日相对状态研究该机制，较高值表示更偏向所述方向。'
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
            B = cross_section_rank((-(values['kdj_k_hfq'] - values['kdj_d_hfq']) / 100).where(eligible))
            X = B
            F = X
        return F.astype(float).replace([np.inf, -np.inf], np.nan).where(eligible).rename_axis(index='date', columns='symbol')
