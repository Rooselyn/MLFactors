"""volume_state_structured_reversal_21d。

r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; order last21days by stock_day.vol; J=lowest6volumedays; K=highest6volumedays; A=Sum(r_s/stock_day.vol[s],s in J)/Sum(1/stock_day.vol[s],s in J); B=Sum(r_s*stock_day.vol[s],s in K)/Sum(stock_day.vol[s],s in K); F=B-A
比较低量确定性运动与高量多空博弈时的加权收益，研究不同成交状态下动量与反转作用的差异。 原文：[高频转低频因子（十）：结构化反转，又一来自桃子姐的因子，IR绝对值超过1！](https://zhuanlan.zhihu.com/p/704104882)。
采用文章实际日频30%阈值、两端各6个收益版本，排除中间9天；原文前段高频概述写“大于10%”但日频段明确两组各6点，本式以该可复现日频段为准。低量组倒数量归一、高量组按量归一，21日价量完整且量正、相同成交量按日期稳定排序。两个分组是中间样本选择，最终为连续收益差，不生成买卖阈值。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol')}
FORMULA = 'r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; order last21days by stock_day.vol; J=lowest6volumedays; K=highest6volumedays; A=Sum(r_s/stock_day.vol[s],s in J)/Sum(1/stock_day.vol[s],s in J); B=Sum(r_s*stock_day.vol[s],s in K)/Sum(stock_day.vol[s],s in K); F=B-A'
RECIPE = {'family': 'volume_state'}

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
    for j in range(c.shape[1]):
        for t in range(20, len(c)):
            rr = r.iloc[t - 20:t + 1, j].to_numpy()
            vol = v['vol'].iloc[t - 20:t + 1, j].to_numpy()
            if not (np.isfinite(rr).all() and np.isfinite(vol).all()) or np.any(vol <= 0):
                continue
            ix = np.argsort(vol, kind='stable')
            (lo, hi) = (ix[:6], ix[-6:])
            out.iat[t, j] = div(np.sum(rr[hi] * vol[hi]), np.sum(vol[hi])) - div(np.sum(rr[lo] / vol[lo]), np.sum(1 / vol[lo]))
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
@fixed_factor('volume_state_structured_reversal_21d', {})
class Factor_volume_state_structured_reversal_21d(BaseFactor):
    name = 'volume_state_structured_reversal_21d'
    description = '比较低量确定性运动与高量多空博弈时的加权收益，研究不同成交状态下动量与反转作用的差异。 原文：[高频转低频因子（十）：结构化反转，又一来自桃子姐的因子，IR绝对值超过1！](https://zhuanlan.zhihu.com/p/704104882)。'
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
