"""daily_ohlc_return_volatility_ratio_21d。

X=All84values(stock_day.open_hfq,stock_day.high_hfq,stock_day.low_hfq,stock_day.close_hfq,last21days); V=Std(X,ddof=1)/Mean(X); F=(stock_day.close_hfq/L21(stock_day.close_hfq)-1)/V
以整段开高低收价格离散程度衡量风险尺度，研究同等价格扰动下累计收益的方向和强度。 原文：[高频转低频因子（九）：21日收益波动比，IC不是很高，回测结果却还不错](https://zhuanlan.zhihu.com/p/703447646)。
采用作者实际使用、明确承认未平方的日频版本，不擅自改回分钟更优波动率的平方口径；样本SD为少量统计约定补全。84个价格及21日前收盘完整、均值和SD正；不把价格水平离散度解释成标准收益波动。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'open_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'open_hfq'), 'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'), 'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'), 'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq')}
FORMULA = 'X=All84values(stock_day.open_hfq,stock_day.high_hfq,stock_day.low_hfq,stock_day.close_hfq,last21days); V=Std(X,ddof=1)/Mean(X); F=(stock_day.close_hfq/L21(stock_day.close_hfq)-1)/V'
RECIPE = {'family': 'ohlc_volatility_ratio'}

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
    arrays = np.stack([v[k].to_numpy() for k in ('open_hfq', 'high_hfq', 'low_hfq', 'close_hfq')])
    out = c * np.nan
    for t in range(20, len(c)):
        a = arrays[:, t - 20:t + 1, :].reshape(84, c.shape[1])
        out.iloc[t] = div(div(c.iloc[t], c.iloc[t - 21]) - 1 if t >= 21 else c.iloc[t] * np.nan, div(a.std(axis=0, ddof=1), a.mean(axis=0)))
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
@fixed_factor('daily_ohlc_return_volatility_ratio_21d', {})
class Factor_daily_ohlc_return_volatility_ratio_21d(BaseFactor):
    name = 'daily_ohlc_return_volatility_ratio_21d'
    description = '以整段开高低收价格离散程度衡量风险尺度，研究同等价格扰动下累计收益的方向和强度。 原文：[高频转低频因子（九）：21日收益波动比，IC不是很高，回测结果却还不错](https://zhuanlan.zhihu.com/p/703447646)。'
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
