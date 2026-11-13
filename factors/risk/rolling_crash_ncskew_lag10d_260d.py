"""rolling_crash_ncskew_lag10d_260d。

r_w=close_hfq[t-5k]/close_hfq[t-5(k+1)]-1,k=0..55; M_w=CrossSectionWeightedMean(r_w,circ_mv at preceding 5-trading-day endpoint); e_w=OLSResidual(r_w ~ 1+M_(w-2)+M_(w-1)+M_w+M_(w+1)+M_(w+2),w=T-53..T-2); W_w=ln(1+e_w); n=Count(W); up={W>Mean(W)}; down={W<Mean(W)}; F=n*(n-1)^1.5*Sum(W^3)/((n-1)*(n-2)*Sum(W^2)^1.5)
通过包含领先滞后市场项的周回归剥离非同步交易影响，再刻画股票特有周收益的负向尾部不对称；输出方向取低崩盘风险较高。 原文：[股价崩盘风险的定义、原理及stata计算方式](https://zhuanlan.zhihu.com/p/697332456)。
每个信号日向后切56个连续5交易日块，滚动52块回归并剔除最近2块（10交易日）目标收益，以保证所需领先两块市场收益已可见；共需281个价格点。市场权重取每块起点流通市值，至少40个有效目标块、设计满秩；1+残差须正，上下行各至少2块。为遵循框架滚动窗口要求，本地不按自然周采样，含义与自然周原版有所变化。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'circ_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'circ_mv')}
FORMULA = 'r_w=close_hfq[t-5k]/close_hfq[t-5(k+1)]-1,k=0..55; M_w=CrossSectionWeightedMean(r_w,circ_mv at preceding 5-trading-day endpoint); e_w=OLSResidual(r_w ~ 1+M_(w-2)+M_(w-1)+M_w+M_(w+1)+M_(w+2),w=T-53..T-2); W_w=ln(1+e_w); n=Count(W); up={W>Mean(W)}; down={W<Mean(W)}; F=n*(n-1)^1.5*Sum(W^3)/((n-1)*(n-2)*Sum(W^2)^1.5)'
RECIPE = {'family': 'weekly_crash', 'variant': 'ncskew'}

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
    out = c * np.nan
    mv = v['circ_mv']
    for t in range(280, len(c)):
        ends = np.arange(t - 280, t + 1, 5)
        prices = c.iloc[ends]
        rr = prices.to_numpy()[1:] / prices.to_numpy()[:-1] - 1
        weights = mv.iloc[ends[:-1]].to_numpy()
        valid = np.isfinite(rr) & np.isfinite(weights) & (weights > 0) & e.iloc[ends[1:]].to_numpy()
        market = np.sum(np.where(valid, rr * weights, 0), axis=1) / np.sum(np.where(valid, weights, 0), axis=1)
        y = rr[2:-2]
        xs = np.column_stack([market[k:k + 52] for k in range(5)])
        for j in range(c.shape[1]):
            good = np.isfinite(y[:, j]) & np.isfinite(xs).all(axis=1)
            a = np.column_stack([np.ones(good.sum()), xs[good]])
            if good.sum() < 40 or np.linalg.matrix_rank(a) < 6:
                continue
            errors = y[good, j] - a @ np.linalg.lstsq(a, y[good, j], rcond=None)[0]
            if np.any(errors <= -1):
                continue
            w = np.log1p(errors)
            n = len(w)
            up = w > w.mean()
            down = w < w.mean()
            out.iat[t, j] = div(n * (n - 1) ** 1.5 * np.sum(w ** 3), (n - 1) * (n - 2) * np.sum(w * w) ** 1.5)
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
@fixed_factor('rolling_crash_ncskew_lag10d_260d', {})
class Factor_rolling_crash_ncskew_lag10d_260d(BaseFactor):
    name = 'rolling_crash_ncskew_lag10d_260d'
    description = '通过包含领先滞后市场项的周回归剥离非同步交易影响，再刻画股票特有周收益的负向尾部不对称；输出方向取低崩盘风险较高。 原文：[股价崩盘风险的定义、原理及stata计算方式](https://zhuanlan.zhihu.com/p/697332456)。'
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
