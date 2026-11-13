"""selfbuilt_peer_joint_cmc_20d。

r_i,s=stock_day.close_hfq[i,s]/stock_day.close_hfq[i,s-1]-1; G_i=stock_day.industry_sw_1[i,d]; m_G,s=Sum_j_in_G(stock_day.total_mv[j,s]*r_j,s)/Sum_j_in_G(stock_day.total_mv[j,s]); for x_i,s over last20days: order ascending x with date tie-break; J5=last5 ordered days; J15=first15 ordered days; U(x)=Sum(w5_k*m_G,J5[k],k=1..5); D(x)=Sum(w15_k*m_G,J15[k],k=1..15); w5=[0.5,0.59,0.7,0.84,1]; w15_k=2^(-(k-1)/14); F=U(r)-D(r)
以文章明确自建的行业成分股收益为参照，研究强弱收益状态下行业共同表现的差异，把个股状态与背后行业环境结合。 原文：[行业联合动量因子，大A对于动量的研究可以说是相当深入了！](https://zhuanlan.zhihu.com/p/2027384893814908858)。
与此前因缺少行业指数而排除的研报原版区分：本来源明确披露使用申万一级成分股按同期总市值加权收益，所以不需字典外的中信/申万指数行情。按代码取20日、当前行业成员重建历史组合，含个股自身、每天至少5只完整有效股，日市值正；20日个股收益完整，量价版本还需量正。权重不归一化，强组按收益升序对应递增w5，弱组对应递减w15。公开代码vol=self.rtn为明显变量误写，量价组明确修为文中定义r×现有vol，不用r²。六个是来源明确的ICM/ICR/VICM/VICR及两种差值，不枚举窗口或权重。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1')}
FORMULA = 'r_i,s=stock_day.close_hfq[i,s]/stock_day.close_hfq[i,s-1]-1; G_i=stock_day.industry_sw_1[i,d]; m_G,s=Sum_j_in_G(stock_day.total_mv[j,s]*r_j,s)/Sum_j_in_G(stock_day.total_mv[j,s]); for x_i,s over last20days: order ascending x with date tie-break; J5=last5 ordered days; J15=first15 ordered days; U(x)=Sum(w5_k*m_G,J5[k],k=1..5); D(x)=Sum(w15_k*m_G,J15[k],k=1..15); w5=[0.5,0.59,0.7,0.84,1]; w15_k=2^(-(k-1)/14); F=U(r)-D(r)'
RECIPE = {'family': 'peer_joint', 'variant': 'cmc'}

def stable_groups(industry, size=None, boundaries=(1 / 3, 2 / 3)):
    """同值按股票代码排序，三组边界使用稳定位置排名。"""
    out = industry.copy().astype('object')
    if size is None:
        return out
    for d in out.index:
        out.loc[d] = None
        for (g, ss) in industry.loc[d].dropna().groupby(industry.loc[d].dropna(), sort=False):
            ids = ss.index[size.loc[d, ss.index].notna()]
            order = size.loc[d, ids].sort_index().sort_values(kind='stable')
            position = (np.arange(len(order)) + 0.5) / max(len(order), 1)
            bins = np.searchsorted(boundaries, position, side='right')
            out.loc[d, order.index] = [f'{g}|{b}' for b in bins]
    return out

def compute_network(recipe, v, e, r):
    family = recipe['family']
    variant = recipe.get('variant', '')
    out = r * np.nan
    n = 20
    industry = v['industry_sw_1']
    size = v.get('total_mv')
    groups = stable_groups(industry, None)
    for t in range(n - 1, len(r)):
        g = groups.iloc[t]
        for (label, ss) in g.dropna().groupby(g.dropna(), sort=False):
            ids = ss.index[e.iloc[t].reindex(ss.index).fillna(False)]
            if len(ids) < 5:
                continue
            rr = r.iloc[t - n + 1:t + 1].loc[:, ids]
            w = size.iloc[t - n + 1:t + 1].loc[:, ids]
            valid = rr.notna() & w.gt(0)
            market = (rr.where(valid) * w.where(valid)).sum(axis=1, min_count=5) / w.where(valid).sum(axis=1, min_count=5)
            for s in ids:
                x = rr[s].to_numpy()
                m = market.to_numpy()
                if not (np.isfinite(x).all() and np.isfinite(m).all()):
                    continue
                order = np.argsort(x, kind='stable')
                u = m[order[-5:]] @ np.array([0.5, 0.59, 0.7, 0.84, 1])
                d = m[order[:15]] @ 2.0 ** (-np.arange(15) / 14)
                out.at[r.index[t], s] = u - d
    return out

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
@fixed_factor('selfbuilt_peer_joint_cmc_20d', {})
class Factor_selfbuilt_peer_joint_cmc_20d(BaseFactor):
    name = 'selfbuilt_peer_joint_cmc_20d'
    description = '以文章明确自建的行业成分股收益为参照，研究强弱收益状态下行业共同表现的差异，把个股状态与背后行业环境结合。 原文：[行业联合动量因子，大A对于动量的研究可以说是相当深入了！](https://zhuanlan.zhihu.com/p/2027384893814908858)。'
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
