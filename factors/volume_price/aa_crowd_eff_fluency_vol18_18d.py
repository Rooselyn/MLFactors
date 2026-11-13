"""aa_crowd_eff_fluency_vol18_18d。

P=(10*stock_day.amount/stock_day.vol)*stock_day.adj_factor; r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; E=abs(P-L17(P))/Sum(abs(P_s-P_(s-1)),s=d-16..d); h=Quantile18(E,0.5); K=Mean(r_s:E_s>=h,last18days)-Mean(r_s:E_s<h,last18days); F=K*M18(1+1000*stock_day.amount/(10000*stock_day.circ_mv))
比较个股高趋势效率和低趋势效率阶段的平均收益，再以成交金额相对流通市值加权，研究价格流畅程度与交易活跃程度的共同作用。 原文：[AlphaAgent公开因子表达式：crowd_eff_fluency_vol18](https://github.com/RndmVariableQ/AlphaAgent/blob/b42cb397025510da44355db9dcf278304321f589/artifacts/factorzoo/stock_1d/expressions/crowd_eff_fluency_vol18.dsl)。
本行AA算子均按已核对公开源码：W_q为当日截面线性分位数q与1−q缩尾；Z为样本标准差ddof=1标准化；Rank为同日平均并列百分位秩；B_n为ln(10000*circ_mv)的同日等频n组（重复边界合并）；N_n(x)=x减同组均值，不是回归残差。各截面至少100只、组内至少5只；未知不填0，分母或标准差为0缺失。EMA_n递推alpha=2/(n+1)、adjust=False、首个有效值为种子，需预读至少100个连续有效日。所有TS均逐股票滚动，要求完整窗口；相比源码min_periods=1为明确的覆盖限制。E的18个价格点只有17个变化，随后再对18个E和收益分组，至少需35个价格点；E各窗路径和须正，两个分组都非空。CROWD_CONTRAST实际是个股时序分组，不是股票截面拥挤度；中位数同值归高组。金额千元、股数手转VWAP系数10；circ_mv是流通市值万元，不是流通股本。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'), 'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'), 'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'), 'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'circ_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'circ_mv'), 'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1')}
FORMULA = 'P=(10*stock_day.amount/stock_day.vol)*stock_day.adj_factor; r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; E=abs(P-L17(P))/Sum(abs(P_s-P_(s-1)),s=d-16..d); h=Quantile18(E,0.5); K=Mean(r_s:E_s>=h,last18days)-Mean(r_s:E_s<h,last18days); F=K*M18(1+1000*stock_day.amount/(10000*stock_day.circ_mv))'
RECIPE = {'family': 'aa', 'variant': 'fluency'}

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

def rank(x, mode='unit', minimum=1, eligible=None):
    x = finite(x)
    if eligible is not None:
        x = x.where(eligible)
    count = x.count(axis=1)
    r = x.rank(axis=1, method='average')
    if mode == 'unit':
        out = div(r.sub(1), count.sub(1).replace(0, np.nan).to_numpy()[:, None])
        out = out.mask(x.notna() & count.eq(1).to_numpy()[:, None], 0.5)
    else:
        out = r.div(count.replace(0, np.nan), axis=0)
    return out.where(count.ge(minimum), axis=0)

def rolling(x, n, method='mean', ddof=0):
    n = int(n)
    if n < 1:
        raise ValueError('滚动窗口必须为正整数')
    roll = x.rolling(n, min_periods=n)
    if method in ('std', 'var'):
        return getattr(roll, method)(ddof=ddof)
    return getattr(roll, method)()

def log(x, base=np.e, offset=0):
    z = x + offset
    if isinstance(z, (pd.DataFrame, pd.Series)):
        z = z.where(z > 0)
    else:
        z = np.where(z > 0, z, np.nan)
    return np.log(z) / np.log(base)

def size_demean(x, size, n, eligible):
    out = x * np.nan
    for d in x.index:
        valid = eligible.loc[d] & x.loc[d].notna() & size.loc[d].gt(0)
        if valid.sum() < 100:
            continue
        groups = pd.qcut(log(size.loc[d, valid]), n, duplicates='drop')
        count = x.loc[d, valid].groupby(groups, observed=True).transform('count')
        out.loc[d, valid] = (x.loc[d, valid] - x.loc[d, valid].groupby(groups, observed=True).transform('mean')).where(count >= 5)
    return out

def winsor(x, q=0.01, mad=None):
    if mad is None:
        return x.clip(x.quantile(q, axis=1), x.quantile(1 - q, axis=1), axis=0)
    m = x.median(axis=1)
    s = x.sub(m, axis=0).abs().median(axis=1) * mad
    clipped = x.clip(m - s, m + s, axis=0)
    return clipped.where(s.ne(0), x, axis=0)

def zscore(x, ddof=0, eligible=None):
    if eligible is not None:
        x = x.where(eligible)
    return x.sub(x.mean(axis=1), axis=0).div(x.std(axis=1, ddof=ddof).replace(0, np.nan), axis=0)

def compute_aa(recipe, v, e, r):
    variant = recipe['variant']
    size = v['circ_mv']
    n = lambda x, k=10: size_demean(x, size, k, e)
    z = lambda x: zscore(x, 1, e)
    rk = lambda x: rank(x, 'pct', 100, e)
    w = lambda x, q=0.01: winsor(x.where(e), q)
    p = div(v['amount'] * 10, v['vol']) * v['adj_factor']
    eff = div(abs(p - p.shift(17)), rolling(abs(p.diff()), 17))
    out = p * np.nan
    for j in range(p.shape[1]):
        for t in range(17, len(p)):
            a = eff.iloc[t - 17:t + 1, j].to_numpy()
            rr = r.iloc[t - 17:t + 1, j].to_numpy()
            if not (np.isfinite(a).all() and np.isfinite(rr).all()):
                continue
            hi = a >= np.quantile(a, 0.5)
            lo = ~hi
            if hi.any() and lo.any():
                out.iat[t, j] = rr[hi].mean() - rr[lo].mean()
    return out * rolling(1 + div(v['amount'] * 1000, size * 10000), 18)

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    return compute_aa(recipe, v, e, r)

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
@fixed_factor('aa_crowd_eff_fluency_vol18_18d', {})
class Factor_aa_crowd_eff_fluency_vol18_18d(BaseFactor):
    name = 'aa_crowd_eff_fluency_vol18_18d'
    description = '比较个股高趋势效率和低趋势效率阶段的平均收益，再以成交金额相对流通市值加权，研究价格流畅程度与交易活跃程度的共同作用。 原文：[AlphaAgent公开因子表达式：crowd_eff_fluency_vol18](https://github.com/RndmVariableQ/AlphaAgent/blob/b42cb397025510da44355db9dcf278304321f589/artifacts/factorzoo/stock_1d/expressions/crowd_eff_fluency_vol18.dsl)。'
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
