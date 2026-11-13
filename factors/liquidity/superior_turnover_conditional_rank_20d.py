"""superior_turnover_conditional_rank_20d。

A=M20(turnover_rate); B=Std20(turnover_rate,ddof=1); X=ln(circ_mv); A0=CSRes(CSZ(WinsorMAD(A,5)),X); B0=CSRes(CSZ(WinsorMAD(B,5)),X); R1=CSRankAscending(B0); G=lower half by R1; R2=RankDescending(A0 within G) if i in G else RankAscending(A0 within complement G); F=-(R1+R2)
根据换手稳定性切换平均换手率的比较方向：稳定组允许较大交易量，不稳定组偏好较小交易量，再合并稳定性得分；最终是多级排序分数而非分组标签。 原文：[优加换手率，有一说一，分层确实变好了！](https://zhuanlan.zhihu.com/p/2078953516727644261)。
先分别缩尾、标准化、市值中性化，再按稳定性分组，不能合成后只中性化一次。缩尾参数来源未给，补为截面中位数±5×MAD，MAD按median(abs(x−median(x)))；流通市值采用已实现量小/量稳子项同口径circ_mv，正值取log，含截距OLS。至少100只完整20日共同有效股票，排名为组内或截面1..N平均秩，分组按稳定排序前floor(N/2)，同值按股票代码；不另收已有的Turn20/STR单项。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'turnover_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate'), 'circ_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'circ_mv')}
FORMULA = 'A=M20(turnover_rate); B=Std20(turnover_rate,ddof=1); X=ln(circ_mv); A0=CSRes(CSZ(WinsorMAD(A,5)),X); B0=CSRes(CSZ(WinsorMAD(B,5)),X); R1=CSRankAscending(B0); G=lower half by R1; R2=RankDescending(A0 within G) if i in G else RankAscending(A0 within complement G); F=-(R1+R2)'
RECIPE = {'family': 'superior_turnover'}

def cs_residual(y, *xs, intercept=True, minimum=None, return_fitted=False):
    out = y * np.nan
    for i in range(len(y)):
        target = y.iloc[i].to_numpy(float)
        xx = np.column_stack([x.iloc[i].to_numpy(float) for x in xs])
        valid = np.isfinite(target) & np.isfinite(xx).all(axis=1)
        if valid.sum() < (minimum or xx.shape[1] + int(intercept)):
            continue
        design = xx[valid]
        if intercept and design.shape[1] == 1 and (np.ptp(design[:, 0]) == 0):
            fitted = np.full(valid.sum(), target[valid].mean())
        else:
            if intercept:
                design = np.column_stack([np.ones(valid.sum()), design])
            if np.linalg.matrix_rank(design) < design.shape[1]:
                continue
            fitted = design @ np.linalg.lstsq(design, target[valid], rcond=None)[0]
        out.iloc[i, np.flatnonzero(valid)] = fitted if return_fitted else target[valid] - fitted
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

def log(x, base=np.e, offset=0):
    z = x + offset
    if isinstance(z, (pd.DataFrame, pd.Series)):
        z = z.where(z > 0)
    else:
        z = np.where(z > 0, z, np.nan)
    return np.log(z) / np.log(base)

def rolling(x, n, method='mean', ddof=0):
    n = int(n)
    if n < 1:
        raise ValueError('滚动窗口必须为正整数')
    roll = x.rolling(n, min_periods=n)
    if method in ('std', 'var'):
        return getattr(roll, method)(ddof=ddof)
    return getattr(roll, method)()

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

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    t = v['turnover_rate']
    size = log(v['circ_mv'])
    a = cs_residual(zscore(winsor(rolling(t, 20).where(e), mad=5)), size)
    b = cs_residual(zscore(winsor(rolling(t, 20, 'std', 1).where(e), mad=5)), size)
    out = t * np.nan
    for d in out.index:
        good = a.loc[d].notna() & b.loc[d].notna() & e.loc[d]
        if good.sum() < 100:
            continue
        bb = b.loc[d, good]
        r1 = bb.rank(method='average')
        order = bb.sort_index().sort_values(kind='stable')
        lower = order.index[:len(order) // 2]
        upper = order.index[len(order) // 2:]
        r2 = pd.concat([a.loc[d, lower].rank(ascending=False), a.loc[d, upper].rank()])
        out.loc[d, r1.index] = -(r1 + r2)
    return out

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
@fixed_factor('superior_turnover_conditional_rank_20d', {})
class Factor_superior_turnover_conditional_rank_20d(BaseFactor):
    name = 'superior_turnover_conditional_rank_20d'
    description = '根据换手稳定性切换平均换手率的比较方向：稳定组允许较大交易量，不稳定组偏好较小交易量，再合并稳定性得分；最终是多级排序分数而非分组标签。 原文：[优加换手率，有一说一，分层确实变好了！](https://zhuanlan.zhihu.com/p/2078953516727644261)。'
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
