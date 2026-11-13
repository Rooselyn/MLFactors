"""Abdi–Ranaldo价差：c=lnC，η=(lnH+lnL)/2；截至日d计算2sqrt(mean_{t=d−20}^{d−1}[(c_t−η_t)(c_t−η_{t+1})])；均值<0截0。

来源: [Abdi–Ranaldo原论文PDF](https://alexandria.unisg.ch/server/api/core/bitstreams/dfb85399-5bcf-465c-8b63-9bfc97ad2ee0/content)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
    'high_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'high_hfq'),
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'low_hfq'),
}


@register_factor
@fixed_factor('rpt_abdi_ranaldo_spread_20d', {})
class Factor_rpt_abdi_ranaldo_spread_20d(BaseFactor):
    name = 'rpt_abdi_ranaldo_spread_20d'
    description = 'Abdi–Ranaldo价差'
    warmup_days = 20
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        c=np.log(x['close_hfq']); eta=(np.log(x['high_hfq'])+np.log(x['low_hfq']))/2
        value = 2*np.sqrt(((c.shift(1)-eta.shift(1))*(c.shift(1)-eta)).rolling(20).mean().clip(lower=0))
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
