"""network_spatial_temporal_centrality_composite_20d。

r_i,d=close_hfq[i,d]/L1(close_hfq[i,d])-1; rho_i=Mean(Corr20(r_i,r_j),j!=i); SCC_i=1/(2*(1-rho_i)); z_i,d=(r_i,d-CSMean(r_d))/CSStd(r_d,ddof=0); TCC_i=1/M20(z_i^2); F=(CSZ(SCC_i)+CSZ(TCC_i))/2
综合股票与其他股票的平均联动性及相对市场偏离的时间稳定性，衡量网络中心程度。两个单项已实现，本行只计公开研究明确提出的标准化等权合成。 原文：[研报复现 ｜ 华西金工-股票网络与网络中心度因子研究](https://zhuanlan.zhihu.com/p/704714725)。
采用华西研究及公开复现的空间/时间中心度定义，不采用另一篇转载误写的最短路径/三角聚类代码。20日完整收益共同股票集合至少100股，股票间相关排除自身；1−rho及M20(z²)须正，截面各标准化分母正，缺单项不以另一项替代。数值大表示更靠中心，经济预期方向偏负，保留来源数值方向。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq')}
FORMULA = 'r_i,d=close_hfq[i,d]/L1(close_hfq[i,d])-1; rho_i=Mean(Corr20(r_i,r_j),j!=i); SCC_i=1/(2*(1-rho_i)); z_i,d=(r_i,d-CSMean(r_d))/CSStd(r_d,ddof=0); TCC_i=1/M20(z_i^2); F=(CSZ(SCC_i)+CSZ(TCC_i))/2'
RECIPE = {'family': 'network'}

def finite(x):
    if isinstance(x, (pd.DataFrame, pd.Series)):
        return x.replace([np.inf, -np.inf], np.nan)
    return np.where(np.isfinite(x), x, np.nan) if np.ndim(x) else x if np.isfinite(x) else np.nan

def div(a, b):
    if isinstance(b, (pd.DataFrame, pd.Series)):
        b = b.where(np.isfinite(b) & b.ne(0))
    elif np.ndim(b):
        b = np.where(np.isfinite(b) & (b != 0), b, np.nan)
    elif not np.isfinite(b) or b == 0:
        b = np.nan
    with np.errstate(all='ignore'):
        return finite(a / b)

def zscore(x, ddof=0, eligible=None):
    if eligible is not None:
        x = x.where(eligible)
    return x.sub(x.mean(axis=1), axis=0).div(x.std(axis=1, ddof=ddof).replace(0, np.nan), axis=0)

def compute_network(recipe, v, e, r):
    family = recipe['family']
    variant = recipe.get('variant', '')
    out = r * np.nan
    temporal = out.copy()
    spatial = out.copy()
    for t in range(19, len(r)):
        a = r.iloc[t - 19:t + 1]
        good = a.notna().all() & e.iloc[t] & a.std().gt(0)
        if good.sum() < 100:
            continue
        values = a.loc[:, good].to_numpy()
        corr = np.corrcoef(values, rowvar=False)
        np.fill_diagonal(corr, np.nan)
        rho = np.nanmean(corr, axis=1)
        spatial.iloc[t, np.flatnonzero(good)] = div(1, 2 * (1 - rho))
        z = div(values - values.mean(axis=1, keepdims=True), values.std(axis=1, keepdims=True))
        temporal.iloc[t, np.flatnonzero(good)] = div(1, np.mean(z * z, axis=0))
    return (zscore(spatial, eligible=e) + zscore(temporal, eligible=e)) / 2

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    return compute_network(recipe, v, e, r)

def daily_values(data, inputs):
    dates = pd.DatetimeIndex(data.index.get_level_values('date').unique()).sort_values()
    symbols = data.index.get_level_values('symbol').unique().sort_values()
    values = {}
    for (key, source) in inputs.items():
        if source.announcement_columns or key not in data:
            continue
        field = data[key].unstack('symbol').reindex(index=dates, columns=symbols)
        if source.field.startswith('industry_sw_'):
            field = field.astype('string').replace('', pd.NA)
        else:
            field = finite(field.apply(pd.to_numeric, errors='coerce').astype(float))
            if source.field in ('open', 'high', 'low', 'close', 'open_hfq', 'high_hfq', 'low_hfq', 'close_hfq', 'adj_factor', 'total_mv', 'circ_mv', 'float_share', 'total_share'):
                field = field.where(field > 0)
            elif source.field in ('vol', 'amount'):
                field = field.where(field >= 0)
        values[key] = field
        values[f"{source.path.split('/')[-3]}.{source.field}"] = field
    return (values, dates, symbols)

@register_factor
@fixed_factor('network_spatial_temporal_centrality_composite_20d', {})
class Factor_network_spatial_temporal_centrality_composite_20d(BaseFactor):
    name = 'network_spatial_temporal_centrality_composite_20d'
    description = '综合股票与其他股票的平均联动性及相对市场偏离的时间稳定性，衡量网络中心程度。两个单项已实现，本行只计公开研究明确提出的标准化等权合成。 原文：[研报复现 ｜ 华西金工-股票网络与网络中心度因子研究](https://zhuanlan.zhihu.com/p/704714725)。'
    INPUTS = INPUTS
    FORMULA = FORMULA
    RECIPE = RECIPE
    warmup_days = 100000
    PRESERVE_REPORT_HISTORY = True

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        (v, dates, symbols) = daily_values(data, self.INPUTS)
        if data.empty:
            return pd.DataFrame(index=dates, columns=symbols, dtype=float)
        e = eligibility(data, dates, symbols)
        recipe = self.RECIPE
        with np.errstate(all='ignore'):
            value = compute_daily(recipe, v, e)
        return finite(value).astype(float).where(e).rename_axis(index='date', columns='symbol')
