"""空间网络中心度：ρ̄_i=mean_{j≠i}corr20(r_i,r_j)；SCC_i=1/[2(1−ρ̄_i)]。

来源: [华西《股票网络与网络中心度因子研究》对应公开复现源码](https://github.com/hugo2046/QuantsPlaybook/blob/master/B-%E5%9B%A0%E5%AD%90%E6%9E%84%E5%BB%BA%E7%B1%BB/%E8%82%A1%E7%A5%A8%E7%BD%91%E7%BB%9C%E4%B8%8E%E7%BD%91%E7%BB%9C%E4%B8%AD%E5%BF%83%E5%BA%A6%E5%9B%A0%E5%AD%90%E7%A0%94%E7%A9%B6/src/factor_algo.py)
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

def peer_mean(frame, minimum, absolute=False, spearman=False):
    corr = frame.rank().corr(min_periods=minimum) if spearman else frame.corr(min_periods=minimum)
    np.fill_diagonal(corr.values, np.nan)
    return (corr.abs() if absolute else corr).mean(axis=1)

@register_factor
@fixed_factor('rpt_hx_spatial_centrality_20d', {})
class Factor_rpt_hx_spatial_centrality_20d(BaseFactor):
    name = 'rpt_hx_spatial_centrality_20d'
    description = '空间网络中心度'
    warmup_days = 20
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        r=x['close_hfq'].pct_change(fill_method=None).where(eligible)
        value=r*np.nan
        for i in range(20,len(dates)):
            window=r.iloc[i-19:i+1]
            value.loc[dates[i]]=1/(2*(1-peer_mean(window,20))).replace(0,np.nan)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
