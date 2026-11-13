"""日间修正反转：[Z(日间波动翻转反转)+Z(日间换手翻转反转)]/2。

来源: [公开实现](https://bigquant.com/data/datasources/hf_prefactors_fz_team_coin)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'open_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'open_hfq'),
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
    'turnover_rate': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'turnover_rate'),
}

def z(x, eligible=None, winsor=False):
    x = x.where(eligible) if eligible is not None else x.copy()
    if winsor:
        x = x.clip(x.quantile(.01, axis=1), x.quantile(.99, axis=1), axis=0)
    return x.sub(x.mean(axis=1), axis=0).div(x.std(axis=1, ddof=1).replace(0, np.nan), axis=0)

def flip(x, eligible):
    difference = x.sub(x.where(eligible).mean(axis=1), axis=0)
    return np.sign(difference).replace(0, 1).where(difference.notna())

def coin(x, eligible):
    c, o, t = x['close_hfq'], x['open_hfq'], x['turnover_rate'] / 100
    r, u = c.pct_change(fill_method=None), c / o - 1
    g = o / c.shift(1) - 1
    distance = g.sub(g.where(eligible).mean(axis=1), axis=0).abs()
    dt = t.diff()
    overnight_turn = dt.shift(1).sub(dt.shift(1).where(eligible).mean(axis=1), axis=0).abs()
    out = {}
    for tag, returns in [('interday', r), ('intraday', u)]:
        out[tag + '_vol_flip'] = flip(returns.rolling(20).std(), eligible) * returns.rolling(20).mean()
        out[tag + '_turn_flip'] = (flip(dt, eligible) * returns).rolling(20).mean()
        out[tag + '_reversal_revised'] = (z(out[tag + '_vol_flip'], eligible) + z(out[tag + '_turn_flip'], eligible)) / 2
    out['overnight_distance'] = distance.rolling(20).mean()
    out['overnight_vol_flip'] = flip(distance.rolling(20).std(), eligible) * distance.rolling(20).mean()
    out['overnight_turn_flip'] = (flip(overnight_turn, eligible) * distance).rolling(20).mean()
    out['overnight_reversal_revised'] = (z(out['overnight_vol_flip'], eligible) + z(out['overnight_turn_flip'], eligible)) / 2
    out['team_coin'] = sum(z(out[tag + '_reversal_revised'], eligible) for tag in ['interday', 'intraday', 'overnight']) / 3
    return out

@register_factor
@fixed_factor('rpt_fz_interday_reversal_revised_20d', {})
class Factor_rpt_fz_interday_reversal_revised_20d(BaseFactor):
    name = 'rpt_fz_interday_reversal_revised_20d'
    description = '日间修正反转'
    warmup_days = 22
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        value = coin(x, eligible)['interday_reversal_revised']
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
