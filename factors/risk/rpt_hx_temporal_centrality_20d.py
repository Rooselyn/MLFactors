"""时间网络中心度：z_{i,d}=(r_{i,d}−mean_cs r_d)/std_cs r_d；TCC_i=1/mean20(z_i²)。

来源: [同一公开复现源码](https://github.com/hugo2046/QuantsPlaybook/blob/master/B-%E5%9B%A0%E5%AD%90%E6%9E%84%E5%BB%BA%E7%B1%BB/%E8%82%A1%E7%A5%A8%E7%BD%91%E7%BB%9C%E4%B8%8E%E7%BD%91%E7%BB%9C%E4%B8%AD%E5%BF%83%E5%BA%A6%E5%9B%A0%E5%AD%90%E7%A0%94%E7%A9%B6/src/factor_algo.py)
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

def z(x, eligible=None, winsor=False):
    x = x.where(eligible) if eligible is not None else x.copy()
    if winsor:
        x = x.clip(x.quantile(.01, axis=1), x.quantile(.99, axis=1), axis=0)
    return x.sub(x.mean(axis=1), axis=0).div(x.std(axis=1, ddof=1).replace(0, np.nan), axis=0)

@register_factor
@fixed_factor('rpt_hx_temporal_centrality_20d', {})
class Factor_rpt_hx_temporal_centrality_20d(BaseFactor):
    name = 'rpt_hx_temporal_centrality_20d'
    description = '时间网络中心度'
    warmup_days = 20
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        r=x['close_hfq'].pct_change(fill_method=None)
        value = 1/z(r,eligible).pow(2).rolling(20).mean().replace(0,np.nan)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
