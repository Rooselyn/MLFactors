"""return_path_distance_peer_equal_21d。

r_i=stock_day.close_hfq/L1(stock_day.close_hfq)-1; m=CSMedian(r); d_ij=sqrt(Sum21((r_i-r_j)^2))/21; F=Mean_j_ne_i(d_ij)
研究近月收益路径的分化及共同风险，衡量与其他股票收益路径的平均欧式距离。 原文：[惊恐度的改进（三）：用欧式距离计算惊恐度，IR继续提高](https://zhuanlan.zhihu.com/p/707074352)。
按原文是欧式距离sqrt(sum平方)再除有效长度，不改为均方根sqrt(sum平方/n)。本地要求21日完整配对、每只股票至少100个完整同伴，因此分母固定21；市场中位每日至少100股，市值正且按信号日d已知值加权。不收需要缺失000985收益的分支；三种参照是来源明确列出的不同研究定义，不为窗口变化扩数。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq')}
FORMULA = 'r_i=stock_day.close_hfq/L1(stock_day.close_hfq)-1; m=CSMedian(r); d_ij=sqrt(Sum21((r_i-r_j)^2))/21; F=Mean_j_ne_i(d_ij)'
RECIPE = {'family': 'path_peer', 'variant': 'equal'}

def compute_network(recipe, v, e, r):
    family = recipe['family']
    variant = recipe.get('variant', '')
    out = r * np.nan
    n = 21
    for t in range(n - 1, len(r)):
        a = r.iloc[t - n + 1:t + 1]
        good = a.notna().all() & e.iloc[t]
        if good.sum() < 2:
            continue
        ar = a.loc[:, good].to_numpy().T
        dist = np.sqrt(np.sum((ar[:, None] - ar[None, :]) ** 2, axis=2)) / 21
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
@fixed_factor('return_path_distance_peer_equal_21d', {})
class Factor_return_path_distance_peer_equal_21d(BaseFactor):
    name = 'return_path_distance_peer_equal_21d'
    description = '研究近月收益路径的分化及共同风险，衡量与其他股票收益路径的平均欧式距离。 原文：[惊恐度的改进（三）：用欧式距离计算惊恐度，IR继续提高](https://zhuanlan.zhihu.com/p/707074352)。'
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
