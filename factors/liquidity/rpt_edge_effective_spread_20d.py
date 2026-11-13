"""EDGE有效价差：o,h,l,c为对数OHLC，m=(h+l)/2；(r1,r2,r3,r4,r5)=(m−o,o−m₋₁,m−c₋₁,c₋₁−m₋₁,o−c₋₁)；τ=1(h≠l或l≠c₋₁)，p_t=Eτ，p_o=E[τ(1(o≠h)+1(o≠l))]，p_c=E[τ(1(c₋₁≠h₋₁)+1(c₋₁≠l₋₁))]；d_j=r_j−E(r_j)τ/p_t；x1=−4d1r2/p_o−4d3r4/p_c，x2=−4d1r5/p_o−4d5r4/p_c；e_j=Ex_j，v_j=mean(x_j²)−e_j²；EDGE=sqrt(abs[(v2e1+v1e2)/(v1+v2)])；总方差≤0改用(e1+e2)/2，其他退化条件按作者代码。 E/Var均取最近20根日K线可得配对；τ有效数<2或p_o/p_c为0则缺失。

来源: [2024年论文与作者项目](https://bidask.eguidotti.com/)；[作者Python源码](https://github.com/eguidotti/bidask/blob/main/python/bidask/edge.py)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'open_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'open_hfq'),
    'high_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'high_hfq'),
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'low_hfq'),
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
}

def edge(ohlc):
    # Ardia, Guidotti and Kroencke: author EDGE, sign=False, 20 daily bars.
    o,h,l,c = np.log(ohlc).T
    m = (h+l)/2
    r1,r2,r3,r4,r5 = m[1:]-o[1:], o[1:]-m[:-1], m[1:]-c[:-1], c[:-1]-m[:-1], o[1:]-c[:-1]
    tau = ((h[1:] != l[1:]) | (l[1:] != c[:-1])).astype(float)
    pt = tau.mean()
    po = (tau*((o[1:] != h[1:]).astype(float)+(o[1:] != l[1:]).astype(float))).mean()
    pc = (tau*((c[:-1] != h[:-1]).astype(float)+(c[:-1] != l[:-1]).astype(float))).mean()
    if tau.sum() < 2 or po == 0 or pc == 0: return np.nan
    d1 = r1-r1.mean()*tau/pt
    d3 = r3-r3.mean()*tau/pt
    d5 = r5-r5.mean()*tau/pt
    x1 = -4*d1*r2/po-4*d3*r4/pc
    x2 = -4*d1*r5/po-4*d5*r4/pc
    e1,e2 = x1.mean(),x2.mean()
    v1,v2 = np.mean(x1*x1)-e1*e1,np.mean(x2*x2)-e2*e2
    squared = (v2*e1+v1*e2)/(v1+v2) if v1+v2>0 else (e1+e2)/2
    return np.sqrt(abs(squared))

@register_factor
@fixed_factor('rpt_edge_effective_spread_20d', {})
class Factor_rpt_edge_effective_spread_20d(BaseFactor):
    name = 'rpt_edge_effective_spread_20d'
    description = 'EDGE有效价差'
    warmup_days = 19
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        value = x['close_hfq']*np.nan
        for symbol in symbols:
            prices=np.column_stack([x[f][symbol] for f in ['open_hfq','high_hfq','low_hfq','close_hfq']])
            for i in range(19,len(dates)):
                window=prices[i-19:i+1]
                if np.isfinite(window).all():value.loc[dates[i],symbol]=edge(window)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
