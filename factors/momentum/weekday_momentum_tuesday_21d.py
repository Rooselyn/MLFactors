"""weekday_momentum_tuesday_21d。

r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; F=Mean(r_d over last21tradingdays with weekday(stock_day.trade_date)=1)
仅聚合周二出现的收益，研究交易周内不同工作日的信息与资金行为能否形成不同的动量来源。 原文：[抱着怀疑的态度，我复现了一下工作日动量，没想到分层回测的结果让我震惊！](https://zhuanlan.zhihu.com/p/2045258810529510083)。
按正文代码在过去21个实际交易日中过滤日历工作日，周一编码0、周五4；至少2个该工作日有效收益，分母为该组实际样本数。节假日不臆造记录，收益用后复权价；每天盘后可用，不借未来同工作日收益。五个组是不同交易日样本而非仅改变滚动长度，不把交易信号阈值作为因子。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq')}
FORMULA = 'r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; F=Mean(r_d over last21tradingdays with weekday(stock_day.trade_date)=1)'
RECIPE = {'family': 'weekday', 'weekday': 1}

def conditional_mean(x, condition, n):
    valid = x.notna() & condition.notna()
    return x.where(condition.eq(1)).rolling(n, min_periods=1).mean().where(valid.rolling(n, min_periods=n).sum().eq(n))

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
    cond = pd.DataFrame(np.broadcast_to((r.index.dayofweek == recipe['weekday'])[:, None], r.shape).astype(float), index=r.index, columns=r.columns)
    return conditional_mean(r, cond, 21)

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
@fixed_factor('weekday_momentum_tuesday_21d', {})
class Factor_weekday_momentum_tuesday_21d(BaseFactor):
    name = 'weekday_momentum_tuesday_21d'
    description = '仅聚合周二出现的收益，研究交易周内不同工作日的信息与资金行为能否形成不同的动量来源。 原文：[抱着怀疑的态度，我复现了一下工作日动量，没想到分层回测的结果让我震惊！](https://zhuanlan.zhihu.com/p/2045258810529510083)。'
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
