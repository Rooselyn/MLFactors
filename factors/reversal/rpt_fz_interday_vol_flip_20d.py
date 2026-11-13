"""日间波动翻转反转：F(std20(r)−mean_cs std20(r))×mean20(r)；F(z)=−1(z<0)，否则+1。

来源: [方正《个股动量效应的识别及“球队硬币”》／实现](https://bigquant.com/data/datasources/hf_prefactors_fz_team_coin)
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
}

def flip(x, eligible):
    difference = x.sub(x.where(eligible).mean(axis=1), axis=0)
    return np.sign(difference).replace(0, 1).where(difference.notna())

@register_factor
@fixed_factor('rpt_fz_interday_vol_flip_20d', {})
class Factor_rpt_fz_interday_vol_flip_20d(BaseFactor):
    name = 'rpt_fz_interday_vol_flip_20d'
    description = '日间波动翻转反转'
    warmup_days = 22
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        b = x['close_hfq'].pct_change(fill_method=None)
        value = flip(b.rolling(20).std(),eligible)*b.rolling(20).mean()
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
