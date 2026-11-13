"""信息离散度滚动移植：W_t={t−251,…,t−21}（231个交易日）；PRET=Π_{d∈W_t}(1+r_d)−1；ID=sign(PRET)×[Σ_W1(r_d<0)−Σ_W1(r_d>0)]/231。12N1明确为12个滚动月中剔除最近1个，不再使用“形成12个月后额外跳1月”的旧口径。

来源: [Da–Gurun–Warachka《Frog in the Pan》PDF](https://academicweb.nd.edu/~zda/Frog.pdf)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
}


@register_factor
@fixed_factor('rpt_dgw_information_discreteness_12N1m', {})
class Factor_rpt_dgw_information_discreteness_12N1m(BaseFactor):
    name = 'rpt_dgw_information_discreteness_12N1m'
    description = '信息离散度滚动移植'
    warmup_days = 253
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        r = x['close_hfq'].pct_change(fill_method=None).shift(21)
        sign_count = ((r<0).astype(float)-(r>0).astype(float)).where(r.notna()).rolling(231).sum()
        pret = (1+r).rolling(231).apply(np.prod, raw=True)-1
        value = np.sign(pret)*sign_count/231
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
