"""凸显性收益滚动移植：逐历史日s_d=abs(r_i,d−mean_cs r_d)/(abs(r_i,d)+abs(mean_cs r_d)+0.1)；在W_t={t−20,…,t}内按s降序取秩k_d（并列平均秩），ω_d=0.7^k_d/Σ_W0.7^k；输出Σ_W(ω_d−1/21)r_i,d。

来源: [Cosemans–Frehen原论文PDF](https://research.tilburguniversity.edu/files/23152071/SalientStocksFMA2017.pdf)；[招商《凸显性收益》原报](https://www.nxny.com/report/view_5156080.html)；[作者机构正式发表版PDF](https://pure.eur.nl/ws/files/47705178/Repub_134044.pdf)
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
@fixed_factor('rpt_cf_salience_return_21d', {})
class Factor_rpt_cf_salience_return_21d(BaseFactor):
    name = 'rpt_cf_salience_return_21d'
    description = '凸显性收益滚动移植'
    warmup_days = 22
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        r = x['close_hfq'].pct_change(fill_method=None)
        market = r.where(eligible).mean(axis=1)
        salience = r.sub(market,axis=0).abs().div(r.abs().add(market.abs(),axis=0)+.1).where(eligible)
        value = r*np.nan
        for symbol in r:
            rr,ss = r[symbol].to_numpy(),salience[symbol].to_numpy()
            for i in range(20,len(rr)):
                a,b=rr[i-20:i+1],ss[i-20:i+1]
                if not (np.isfinite(a).all() and np.isfinite(b).all()): continue
                weights = .7**pd.Series(b).rank(ascending=False,method='average').to_numpy()
                value.loc[dates[i],symbol] = np.dot(weights/weights.sum()-1/21,a)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
