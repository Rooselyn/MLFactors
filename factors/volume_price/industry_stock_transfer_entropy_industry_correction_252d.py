"""industry_stock_transfer_entropy_industry_correction_252d。

r_i,s=stock_day.close_hfq[i,s]/stock_day.close_hfq[i,s-1]-1; G_d=stock_day.industry_sw_1 on signal d; M_G,s=Sum_G(stock_day.total_mv[s]*r_s)/Sum_G(stock_day.total_mv[s]); S_i,s=I(r_i,s>0); Z_s=I(M_G,s>0); use triples(S_s,S_(s+1),Z_s),s=d-251..d-1; p_abc=Count(triple=(a,b,c))/Count(valid triples); p_b_a=Count(S_s=a,S_(s+1)=b)/Count(S_s=a); p_b_ac=Count(triple=(a,b,c))/Count(S_s=a,Z_s=c); T=Sum(p_abc*ln(p_b_ac/p_b_a),over p_abc>0); E0=2*p_(b=1)_a(S_d)-1; E1=2*p_(b=1)_ac(S_d,Z_d)-1; Delta=E0-E1; F=Delta
以已发生的历史股票和同行业自建组合收益状态估计，衡量行业条件加入前后方向预测的差异；输入状态0/1不作为最终排序值。 原文：[基于转移熵的行业信息传导，这个刚出炉的研报值得我用4000字来深聊吗？](https://zhuanlan.zhihu.com/p/2076779090506522813)。
来源代码明确用同组股票同期市值加权收益自建行业状态，不要求缺失的行业指数行情。补定窗口为最近252个日收益、251组已知后继；用d日当前行业分组对该历史窗口重新聚合，各日市值逐日对应，每行业至少5股。未知收益先缺失再比较，不将NaN>0当跌；至少200有效三元组，当前a及(a,c)条件各至少10条，否则该条件预测缺失。0联合概率不入log，条件概率按出现次数归一化，不把从未见过条件用0填补。待预测S_(d+1)从未读取；训练后继最大到d，盘后可用。窗口未披露属于明示参数补全；Delta按公开代码E0−E1，和正文“条件−基准”相反，采用代码。只有条件概率和信息量输出，不是买卖分类标签。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1')}
FORMULA = 'r_i,s=stock_day.close_hfq[i,s]/stock_day.close_hfq[i,s-1]-1; G_d=stock_day.industry_sw_1 on signal d; M_G,s=Sum_G(stock_day.total_mv[s]*r_s)/Sum_G(stock_day.total_mv[s]); S_i,s=I(r_i,s>0); Z_s=I(M_G,s>0); use triples(S_s,S_(s+1),Z_s),s=d-251..d-1; p_abc=Count(triple=(a,b,c))/Count(valid triples); p_b_a=Count(S_s=a,S_(s+1)=b)/Count(S_s=a); p_b_ac=Count(triple=(a,b,c))/Count(S_s=a,Z_s=c); T=Sum(p_abc*ln(p_b_ac/p_b_a),over p_abc>0); E0=2*p_(b=1)_a(S_d)-1; E1=2*p_(b=1)_ac(S_d,Z_d)-1; Delta=E0-E1; F=Delta'
RECIPE = {'family': 'industry_entropy', 'variant': 'correction'}

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
    n = 252
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
                valid = np.isfinite(x) & np.isfinite(m)
                a = x[:-1] > 0
                b = x[1:] > 0
                c = m[:-1] > 0
                ok = valid[:-1] & valid[1:]
                if ok.sum() < 200 or not valid[-1]:
                    continue
                counts = np.zeros((2, 2, 2))
                for (aa, bb, cc) in zip(a[ok], b[ok], c[ok]):
                    counts[int(aa), int(bb), int(cc)] += 1
                ac = counts.sum(axis=1)
                ab = counts.sum(axis=2)
                pa = ab.sum(axis=1)
                total = counts.sum()
                te = 0.0
                for (aa, bb, cc) in np.ndindex(2, 2, 2):
                    z = counts[aa, bb, cc]
                    if z > 0:
                        te += z / total * np.log(z / ac[aa, cc] / (ab[aa, bb] / pa[aa]))
                aa = int(x[-1] > 0)
                cc = int(m[-1] > 0)
                if pa[aa] < 10 or ac[aa, cc] < 10:
                    continue
                e0 = 2 * ab[aa, 1] / pa[aa] - 1
                e1 = 2 * counts[aa, 1, cc] / ac[aa, cc] - 1
                delta = e0 - e1
                out.at[r.index[t], s] = {'entropy': te, 'base': e0, 'correction': delta, 'combined': e0 + delta * te}[variant]
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
@fixed_factor('industry_stock_transfer_entropy_industry_correction_252d', {})
class Factor_industry_stock_transfer_entropy_industry_correction_252d(BaseFactor):
    name = 'industry_stock_transfer_entropy_industry_correction_252d'
    description = '以已发生的历史股票和同行业自建组合收益状态估计，衡量行业条件加入前后方向预测的差异；输入状态0/1不作为最终排序值。 原文：[基于转移熵的行业信息传导，这个刚出炉的研报值得我用4000字来深聊吗？](https://zhuanlan.zhihu.com/p/2076779090506522813)。'
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
