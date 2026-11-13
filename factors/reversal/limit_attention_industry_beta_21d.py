"""limit_attention_industry_beta_21d。

r=close_hfq/L1(close_hfq)-1; A=GroupMean(I(limit_status in {2,3,5,6}),industry_sw_1); b=OLSCoef(r ~ 1+A+FFLocalMKT+FFLocalSMB+FFLocalHML+FFLocalUMD,last 21d); F=-abs(b_A)
衡量个股对所属行业涨跌停密集事件的超额敏感度，控制规模、价值和动量收益后，研究注意力捕捉与过度买盘造成的偏贵。输入状态是离散值，最终回归系数为连续数值。 原文：[基于异常收益率的注意力捕捉，一个结合了涨跌停数量、Fama-French三因子模型和动量的超复杂因子！](https://zhuanlan.zhihu.com/p/1997453163918287099)。
以字典收盘状态2/3/5/6识别涨跌停，未知-1不进入占比分母；同日市场至少100股、行业至少10股。21日共同有效样本至少16且满秩，否则缺失。按正文分别只放一个关注度解释量，修正原代码重复列索引；UMD按正文用L21(close_hfq)/L252(close_hfq)-1，修正原代码反向价格比。FFLocal控制组合详见公共约定。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'pb': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pb'), 'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1'), 'limit_status': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'limit_status')}
FORMULA = 'r=close_hfq/L1(close_hfq)-1; A=GroupMean(I(limit_status in {2,3,5,6}),industry_sw_1); b=OLSCoef(r ~ 1+A+FFLocalMKT+FFLocalSMB+FFLocalHML+FFLocalUMD,last 21d); F=-abs(b_A)'
RECIPE = {'family': 'ff_attention', 'variant': 'limit_industry'}

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

def group_transform(x, groups, method='mean', ddof=0):
    out = x * np.nan
    for d in x.index:
        g = groups.loc[d]
        valid = g.notna() & g.ne('')
        (xx, gg) = (x.loc[d, valid], g[valid])
        if method == 'rank':
            rr = xx.groupby(gg).rank(method='average')
            nn = xx.groupby(gg).transform('count')
            y = (rr - 1) / (nn - 1).replace(0, np.nan)
            y = y.mask(xx.notna() & nn.eq(1), 0.5)
        elif method == 'z':
            y = (xx - xx.groupby(gg).transform('mean')) / xx.groupby(gg).transform('std', ddof=ddof).replace(0, np.nan)
        else:
            y = xx.groupby(gg).transform(method, **{'ddof': ddof} if method == 'std' else {})
        out.loc[d, valid] = y
    return out

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
    status = v['limit_status']
    attention = status.isin([2, 3, 5, 6]).astype(float).where(status.isin(range(7)))
    raw = attention.where(e)
    attention = group_transform(raw, v['industry_sw_1']).where(group_transform(raw, v['industry_sw_1'], 'count') >= 10)
    return -abs(window_ols(r, [attention, *ff], 21, 'coef', coefficient=1, minimum=16))

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
@fixed_factor('limit_attention_industry_beta_21d', {})
class Factor_limit_attention_industry_beta_21d(BaseFactor):
    name = 'limit_attention_industry_beta_21d'
    description = '衡量个股对所属行业涨跌停密集事件的超额敏感度，控制规模、价值和动量收益后，研究注意力捕捉与过度买盘造成的偏贵。输入状态是离散值，最终回归系数为连续数值。 原文：[基于异常收益率的注意力捕捉，一个结合了涨跌停数量、Fama-French三因子模型和动量的超复杂因子！](https://zhuanlan.zhihu.com/p/1997453163918287099)。'
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
