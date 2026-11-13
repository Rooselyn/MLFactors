"""Corwin–Schultz基础价差：β=ln²(H_t/L_t)+ln²(H_{t−1}/L_{t−1})，γ=ln²[max(H_t,H_{t−1})/min(L_t,L_{t−1})]；α=[sqrt(2β)−sqrt(β)]/(3−2sqrt2)−sqrt[γ/(3−2sqrt2)]；S=2(exp(α)−1)/(1+exp(α))；本目录采用未调隔夜缺口基础式，负S截0。

来源: [Corwin–Schultz原论文](https://onlinelibrary.wiley.com/doi/pdf/10.1111/j.1540-6261.2012.01729.x)；[教授公开公式讲义](https://ba-odegaard.no/teach/notes/liquidity_estimators/corwin_schultz_high_low_estimator/slides_high_low.pdf)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'high_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'high_hfq'),
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'low_hfq'),
}


@register_factor
@fixed_factor('rpt_corwin_schultz_base_spread_2d', {})
class Factor_rpt_corwin_schultz_base_spread_2d(BaseFactor):
    name = 'rpt_corwin_schultz_base_spread_2d'
    description = 'Corwin–Schultz基础价差'
    warmup_days = 1
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        h,l=x['high_hfq'],x['low_hfq']
        beta=np.log(h/l)**2+np.log(h.shift(1)/l.shift(1))**2
        gamma=np.log(np.maximum(h,h.shift(1))/np.minimum(l,l.shift(1)))**2
        a=(np.sqrt(2*beta)-np.sqrt(beta))/(3-2*np.sqrt(2))-np.sqrt(gamma/(3-2*np.sqrt(2)))
        value = (2*np.tanh(a/2)).clip(lower=0)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
