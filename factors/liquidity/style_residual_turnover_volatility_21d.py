"""style_residual_turnover_volatility_21d。

T=turnover_rate; U=close_hfq/L21(close_hfq)-1; X1=CSMean(T); X2=Mean(T in largest total_mv tercile)-Mean(T in smallest tercile); X3=Mean(T in smallest pb tercile)-Mean(T in largest tercile); X4=Mean(T in smallest U tercile)-Mean(T in largest tercile); e=OLSResidual(T ~ 1+X1+X2+X3+X4,last 21d); F=-Std(e,ddof=0)
从换手率中剥离全市场与规模、账面估值、收益动量分组的共同换手变化，偏好个股特异交易活动较稳定者；不同于换手率原始标准差或仅剥离市值的截面波动。 原文：[特质换手率波动，当Fama-French模型和换手率结合，居然有6年IC绝对值超过0.1！](https://zhuanlan.zhihu.com/p/1999239989175787836)。
采用文章复现的同期解释变量，不沿用研报前一期的另一版本；分组每日按四项字段共同有效股票取整三分位，每端至少20家，pb及市值正。21日回归至少16共同有效日且满秩，残差用总体标准差；修正原代码局部变量引用笔误，不复用其错误索引。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'turnover_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate'), 'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'pb': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pb')}
FORMULA = 'T=turnover_rate; U=close_hfq/L21(close_hfq)-1; X1=CSMean(T); X2=Mean(T in largest total_mv tercile)-Mean(T in smallest tercile); X3=Mean(T in smallest pb tercile)-Mean(T in largest tercile); X4=Mean(T in smallest U tercile)-Mean(T in largest tercile); e=OLSResidual(T ~ 1+X1+X2+X3+X4,last 21d); F=-Std(e,ddof=0)'
RECIPE = {'family': 'style_turnover'}

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

def ff_local(v, eligible):
    (c, mv, pb) = (v['close_hfq'], v['total_mv'], v['pb'])
    r = div(c, c.shift(1)) - 1
    good = eligible & r.notna() & mv.gt(0) & pb.gt(0)
    controls = {n: r * np.nan for n in ('MKT', 'SMB', 'HML', 'UMD')}
    mom = div(c.shift(21), c.shift(252)) - 1
    for d in r.index:
        ids = r.columns[good.loc[d]]
        if len(ids) < 60:
            continue
        size = mv.loc[d, ids].sort_index().sort_values(kind='stable')
        small = size.index[:len(size) // 2]
        big = size.index[len(size) // 2:]

        def vw(ss):
            w = mv.loc[d, ss]
            return (w * r.loc[d, ss]).sum() / w.sum() if len(ss) else np.nan
        mkt = vw(ids)
        cells = []
        for ss in (small, big):
            bp = div(1, pb.loc[d, ss]).sort_index().sort_values(kind='stable')
            n = len(bp)
            split = (int(np.ceil(0.3 * n)), int(np.ceil(0.7 * n)))
            bins = [bp.index[:split[0]], bp.index[split[0]:split[1]], bp.index[split[1]:]]
            cells.extend((vw(s) if len(s) >= 10 else np.nan for s in bins))
        (sl, sm, sh, bl, bm, bh) = cells
        for (name, x) in [('MKT', mkt), ('SMB', (sl + sm + sh - bl - bm - bh) / 3), ('HML', (sh + bh - sl - bl) / 2)]:
            controls[name].loc[d] = x
        mo = mom.loc[d, ids].dropna().sort_index().sort_values(kind='stable')
        n = int(np.floor(0.3 * len(mo)))
        if n >= 20:
            controls['UMD'].loc[d] = vw(mo.index[-n:]) - vw(mo.index[:n])
    return (r, controls)

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

def window_ols(y, xs, n, kind='last_residual', coefficient=-1, ridge=0, minimum=None):
    """完整窗口OLS。常数/共线解释量不以伪逆制造不唯一系数。"""
    out = y * np.nan
    for j in range(y.shape[1]):
        yy = y.iloc[:, j].to_numpy(float)
        xx = np.column_stack([x.iloc[:, j].to_numpy(float) for x in xs])
        for i in range(n - 1, len(y)):
            (a, b) = (yy[i - n + 1:i + 1], xx[i - n + 1:i + 1])
            valid = np.isfinite(a) & np.isfinite(b).all(axis=1)
            if valid.sum() < (n if minimum is None else minimum) or not valid[-1]:
                continue
            (a, b) = (a[valid], b[valid])
            design = np.column_stack([np.ones(len(a)), b])
            if np.linalg.matrix_rank(design) < design.shape[1] and ridge == 0:
                continue
            if ridge:
                penalty = np.eye(design.shape[1]) * ridge
                penalty[0, 0] = 0
                beta = np.linalg.solve(design.T @ design + penalty, design.T @ a)
            else:
                beta = np.linalg.lstsq(design, a, rcond=None)[0]
            e = a - design @ beta
            if kind == 'coef':
                v = beta[coefficient]
            elif kind == 'std':
                v = e.std(ddof=0)
            elif kind == 'fitted':
                v = (design @ beta)[-1]
            else:
                v = e[-1]
            out.iat[i, j] = v
    return out

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    cached = v.get('_ff_local')
    if cached is None:
        (r, controls) = ff_local(v, e)
    else:
        (full_r, full_controls) = cached
        r = full_r.reindex(index=c.index, columns=c.columns)
        controls = {k: x.reindex(index=c.index, columns=c.columns) for (k, x) in full_controls.items()}
    ff = [controls[k] for k in ('MKT', 'SMB', 'HML', 'UMD')]
    t = v['turnover_rate']
    u = div(c, c.shift(21)) - 1
    xs = [t.where(e) * 0 + t.where(e).mean(axis=1).to_numpy()[:, None]]
    for (key, sign) in [('total_mv', 1), ('pb', -1), ('momentum', -1)]:
        field = u if key == 'momentum' else v[key]
        ranks = rank(field, eligible=e)
        low = t.where(e & ranks.le(1 / 3)).mean(axis=1)
        high = t.where(e & ranks.ge(2 / 3)).mean(axis=1)
        xs.append(t * 0 + (sign * (high - low)).to_numpy()[:, None])
    return -window_ols(t, xs, 21, 'std')

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
@fixed_factor('style_residual_turnover_volatility_21d', {})
class Factor_style_residual_turnover_volatility_21d(BaseFactor):
    name = 'style_residual_turnover_volatility_21d'
    description = '从换手率中剥离全市场与规模、账面估值、收益动量分组的共同换手变化，偏好个股特异交易活动较稳定者；不同于换手率原始标准差或仅剥离市值的截面波动。 原文：[特质换手率波动，当Fama-French模型和换手率结合，居然有6年IC绝对值超过0.1！](https://zhuanlan.zhihu.com/p/1999239989175787836)。'
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
