"""hurst_rescaled_range_256d。

x=ln(close_hfq/L1(close_hfq)); for n in {8,16,32,64,128}: partition last 256 x into 256/n nonoverlap blocks; Z_b,k=Sum(x_b,j-Mean(x_b),j=1..k); RS_n=Mean_b((Max(Z_b)-Min(Z_b))/Std(x_b,ddof=0)); F=OLS_slope(ln(RS_n) ~ 1+ln(n))
通过多尺度重标极差估计收益路径的长记忆性，高值表示较强持续性、低值偏均值回复；本身不提供上涨方向，也不把入场金叉条件作为输出。 原文：[基于赫斯特指数的策略研究](https://zhuanlan.zhihu.com/p/33579159)。
原文未给局部估计窗口与分割尺度，补为256日和8至128的五个二倍尺度，至少各尺度75%子块非退化且不少于2块。零标准差或极差0子块不参与，至少4个有效尺度；回归采用首个经验式RS=C*n^H的正斜率，修正文中对数式的负号笔误。需256完整有效日收益。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq')}
FORMULA = 'x=ln(close_hfq/L1(close_hfq)); for n in {8,16,32,64,128}: partition last 256 x into 256/n nonoverlap blocks; Z_b,k=Sum(x_b,j-Mean(x_b),j=1..k); RS_n=Mean_b((Max(Z_b)-Min(Z_b))/Std(x_b,ddof=0)); F=OLS_slope(ln(RS_n) ~ 1+ln(n))'
RECIPE = {'family': 'hurst'}

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

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None

    def calc(a):
        xx = []
        yy = []
        for n in (8, 16, 32, 64, 128):
            blocks = a.reshape(-1, n)
            z = np.cumsum(blocks - blocks.mean(axis=1, keepdims=True), axis=1)
            ranges = np.ptp(z, axis=1)
            sd = blocks.std(axis=1)
            good = (ranges > 0) & (sd > 0)
            if good.sum() >= max(2, int(np.ceil(0.75 * len(blocks)))):
                xx.append(np.log(n))
                yy.append(np.log(np.mean(ranges[good] / sd[good])))
        return np.polyfit(xx, yy, 1)[0] if len(xx) >= 4 else np.nan
    return log(div(c, c.shift(1))).rolling(256, min_periods=256).apply(calc, raw=True)

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
@fixed_factor('hurst_rescaled_range_256d', {})
class Factor_hurst_rescaled_range_256d(BaseFactor):
    name = 'hurst_rescaled_range_256d'
    description = '通过多尺度重标极差估计收益路径的长记忆性，高值表示较强持续性、低值偏均值回复；本身不提供上涨方向，也不把入场金叉条件作为输出。 原文：[基于赫斯特指数的策略研究](https://zhuanlan.zhihu.com/p/33579159)。'
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
