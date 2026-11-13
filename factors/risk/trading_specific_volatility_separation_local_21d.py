"""trading_specific_volatility_separation_local_21d。

r=close_hfq/L1(close_hfq)-1; SIGMA_t=Std(OLSResidual(r~1+FFLocalMKT+FFLocalSMB+FFLocalHML+FFLocalUMD,last 21d),ddof=0); L=M21(SIGMA); X=(ln(total_mv),1/pe,pb/pe,close_hfq/L21(close_hfq)-1); D=OLS_FittedCurrent(SIGMA~1+X,last 21d); F=SIGMA-L-D
将四因子无法解释的股票收益波动进一步拆为自身常态与规模、估值、盈利和动量可解释部分，观察剩余的异质交易波动。 原文：[把特质波动率拆开以后，因子表现炸裂提升？](https://zhuanlan.zhihu.com/p/2096348740156239932)。
公开正文明确两次21日含截距时序回归与中间21日均值，SIGMA为同一次回归整段窗口残差标准差，不能拼接各窗最后残差再求波动。市场控制采用已展开的FFLocal，原文额外日无风险利率不在字典，本地固定r_f=0作为明示收益基准参数，不编造利率字段或声称官方Carhart原值。每次至少15有效日且满秩，总市值正、PE非0，PB/PE按来源日频代理，非财报ROE；L至少17值，未填补未知风险因子。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'pb': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pb'), 'pe': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pe')}
FORMULA = 'r=close_hfq/L1(close_hfq)-1; SIGMA_t=Std(OLSResidual(r~1+FFLocalMKT+FFLocalSMB+FFLocalHML+FFLocalUMD,last 21d),ddof=0); L=M21(SIGMA); X=(ln(total_mv),1/pe,pb/pe,close_hfq/L21(close_hfq)-1); D=OLS_FittedCurrent(SIGMA~1+X,last 21d); F=SIGMA-L-D'
RECIPE = {'family': 'specific_separation'}

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

def log(x, base=np.e, offset=0):
    z = x + offset
    if isinstance(z, (pd.DataFrame, pd.Series)):
        z = z.where(z > 0)
    else:
        z = np.where(z > 0, z, np.nan)
    return np.log(z) / np.log(base)

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
    sigma = window_ols(r, ff, 21, 'std', minimum=15)
    xs = [log(v['total_mv']), div(1, v['pe']), div(v['pb'], v['pe']), div(c, c.shift(21)) - 1]
    d = window_ols(sigma, xs, 21, 'fitted', minimum=15)
    return sigma - sigma.rolling(21, min_periods=17).mean() - d

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
@fixed_factor('trading_specific_volatility_separation_local_21d', {})
class Factor_trading_specific_volatility_separation_local_21d(BaseFactor):
    name = 'trading_specific_volatility_separation_local_21d'
    description = '将四因子无法解释的股票收益波动进一步拆为自身常态与规模、估值、盈利和动量可解释部分，观察剩余的异质交易波动。 原文：[把特质波动率拆开以后，因子表现炸裂提升？](https://zhuanlan.zhihu.com/p/2096348740156239932)。'
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
