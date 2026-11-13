"""peer_relative_fear_21d。

r_i=stock_day.close_hfq/L1(stock_day.close_hfq)-1; D_i=Mean_j_ne_i(abs(r_i-r_j)/(abs(r_i)+abs(r_j)+0.1)); F=M21(D_i)
把所有其他股票逐一作为参照，衡量个股相对整个收益横截面的分化强度，避免单一市场中枢压缩分布信息。 原文：[惊恐度因子改进（二）：名字想不出来，IR绝对值首次突破1](https://zhuanlan.zhihu.com/p/706862901)。
每个信号日仅用有效其他股票至少100只、等权求平均，剔除自身。按照作者实际展示的等权版本收一项，不枚举其仅建议尝试的总/流通市值加权；0.1与收益小数尺度保持引用原式，21日至少17有效日。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq')}
FORMULA = 'r_i=stock_day.close_hfq/L1(stock_day.close_hfq)-1; D_i=Mean_j_ne_i(abs(r_i-r_j)/(abs(r_i)+abs(r_j)+0.1)); F=M21(D_i)'
RECIPE = {'family': 'peer_fear'}

def compute_network(recipe, v, e, r):
    family = recipe['family']
    variant = recipe.get('variant', '')
    out = r * np.nan
    n = 1
    for t in range(n - 1, len(r)):
        a = r.iloc[t - n + 1:t + 1]
        good = a.notna().all() & e.iloc[t]
        if good.sum() < 2:
            continue
        ar = a.loc[:, good].to_numpy().T
        dist = abs(ar - ar.T) / (abs(ar) + abs(ar.T) + 0.1)
        np.fill_diagonal(dist, np.nan)
        result = np.nanmean(dist, axis=1)
        out.iloc[t, np.flatnonzero(good)] = result
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
@fixed_factor('peer_relative_fear_21d', {})
class Factor_peer_relative_fear_21d(BaseFactor):
    name = 'peer_relative_fear_21d'
    description = '把所有其他股票逐一作为参照，衡量个股相对整个收益横截面的分化强度，避免单一市场中枢压缩分布信息。 原文：[惊恐度因子改进（二）：名字想不出来，IR绝对值首次突破1](https://zhuanlan.zhihu.com/p/706862901)。'
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
