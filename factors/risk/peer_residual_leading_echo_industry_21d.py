"""peer_residual_leading_echo_industry_21d。

r=close_hfq/L1(close_hfq)-1; G=industry_sw_1; m_s=Sum(L1(total_mv)_j,s*r_j,s,j in G)/Sum(L1(total_mv)_j,s,j in G); b_i=Cov(r_i,m,last 21d)/Var(m,last 21d); e_i,s=r_i,s-b_i*m_s; C_k=Corr(e_i,s,m_(s+k),s=t-20..t-k),k=1,2,3; F=-Mean(C_1,C_2,C_3)
以同一行业作为可比参照，剔除同期收益暴露后观察个股残差与后续同类收益的回声，研究相对信息传导和拥挤关联。 原文：[把codex设计的选基因子，加上这个黑科技后，选股的多空收益大幅提高！](https://zhuanlan.zhihu.com/p/2093086253512246192)。
同类收益按来源设计直接由项目股票和前日市值构造，不调用不存在的行业指数；每个信号日固定当日行业/市值组，在已结束21日内回算该组参照序列，不使用信号日后的m。组内至少5股、每股至少15有效日；剔除abs(r)>0.20记录为缺失，不作0或截断。均值协方差在共同有效样本上计算，b去均值估计，但e按原文不额外扣截距；三个相关各至少10有效对，至少2个有效相关才平均；市场基准方差正。市值层按当日组内三等分，边界同值按股票代码稳定分组；不是将基金净值当成股票数据。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1')}
FORMULA = 'r=close_hfq/L1(close_hfq)-1; G=industry_sw_1; m_s=Sum(L1(total_mv)_j,s*r_j,s,j in G)/Sum(L1(total_mv)_j,s,j in G); b_i=Cov(r_i,m,last 21d)/Var(m,last 21d); e_i,s=r_i,s-b_i*m_s; C_k=Corr(e_i,s,m_(s+k),s=t-20..t-k),k=1,2,3; F=-Mean(C_1,C_2,C_3)'
RECIPE = {'family': 'peer_echo', 'variant': 'industry'}

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
    n = 21
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
            w = size.shift(1).iloc[t - n + 1:t + 1].loc[:, ids]
            rr = rr.where(abs(rr) <= 0.2)
            valid = rr.notna() & w.gt(0)
            market = (rr.where(valid) * w.where(valid)).sum(axis=1, min_count=5) / w.where(valid).sum(axis=1, min_count=5)
            for s in ids:
                x = rr[s].to_numpy()
                m = market.to_numpy()
                ok = np.isfinite(x) & np.isfinite(m)
                if ok.sum() < 15 or np.var(m[ok]) == 0:
                    continue
                beta = np.cov(x[ok], m[ok], ddof=0)[0, 1] / np.var(m[ok])
                res = x - beta * m
                corr = []
                for k in (1, 2, 3):
                    (aa, bb) = (res[:-k], m[k:])
                    good = np.isfinite(aa) & np.isfinite(bb)
                    if good.sum() >= 10 and np.std(aa[good]) > 0 and (np.std(bb[good]) > 0):
                        corr.append(np.corrcoef(aa[good], bb[good])[0, 1])
                if len(corr) >= 2:
                    out.at[r.index[t], s] = -np.mean(corr)
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
@fixed_factor('peer_residual_leading_echo_industry_21d', {})
class Factor_peer_residual_leading_echo_industry_21d(BaseFactor):
    name = 'peer_residual_leading_echo_industry_21d'
    description = '以同一行业作为可比参照，剔除同期收益暴露后观察个股残差与后续同类收益的回声，研究相对信息传导和拥挤关联。 原文：[把codex设计的选基因子，加上这个黑科技后，选股的多空收益大幅提高！](https://zhuanlan.zhihu.com/p/2093086253512246192)。'
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
