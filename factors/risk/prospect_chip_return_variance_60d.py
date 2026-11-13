"""prospect_chip_return_variance_60d。

u_s=clip(turnover_rate[s]/100,0,1); a_s=u_s*Prod(1-u_k,k=s+1..t); w_s=a_s/Sum(a_s); x_s=(close_hfq[t]-close_hfq[s])/close_hfq[t]; m=Sum(w_s*x_s); v=Sum(w_s*(x_s-m)^2); F=-v
以每日换手后的残存概率重建近60日成本收益分布，偏好相对成本更集中的股票。输入为历史路径推断的筹码，区别于直接读取当日筹码价档；也不等于总收益波动率。 原文：[破解处置效应：基于前景理论的筹码四阶矩因子构建与量化实证](https://zhuanlan.zhihu.com/p/2084953142454764201)。
窗口按源码取60交易日，权重和为0时缺失；方向取负以对应低分歧。未另计同一构造的一阶成本突出量，避免与已有资本利得突出量机制重复。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'turnover_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate')}
FORMULA = 'u_s=clip(turnover_rate[s]/100,0,1); a_s=u_s*Prod(1-u_k,k=s+1..t); w_s=a_s/Sum(a_s); x_s=(close_hfq[t]-close_hfq[s])/close_hfq[t]; m=Sum(w_s*x_s); v=Sum(w_s*(x_s-m)^2); F=-v'
RECIPE = {'family': 'chip_moments', 'variant': 'variance'}

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
    window = 60
    p = c
    u = (v['turnover_rate'] / 100).clip(0, 1)
    out = p * np.nan
    for j in range(p.shape[1]):
        (pp, uu) = (p.iloc[:, j].to_numpy(float), u.iloc[:, j].to_numpy(float))
        for t in range(window - 1, len(p)):
            price = pp[t - window + 1:t + 1]
            turn = uu[t - window + 1:t + 1]
            if not (np.isfinite(price).all() and np.isfinite(turn).all()) or np.any(price <= 0):
                continue
            survive = np.r_[np.cumprod(1 - turn[:0:-1])[::-1], 1.0]
            w = turn * survive
            if w.sum() <= 0:
                continue
            w = w / w.sum()
            x = (pp[t] - price) / pp[t]
            m = w @ x
            variance = w @ (x - m) ** 2
            k = {'variance': 2, 'skew': 3, 'kurtosis': 4}[variant]
            out.iat[t, j] = -variance if k == 2 else div(w @ (x - m) ** k, variance ** (k / 2)) * (1 if k == 3 else -1)
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
@fixed_factor('prospect_chip_return_variance_60d', {})
class Factor_prospect_chip_return_variance_60d(BaseFactor):
    name = 'prospect_chip_return_variance_60d'
    description = '以每日换手后的残存概率重建近60日成本收益分布，偏好相对成本更集中的股票。输入为历史路径推断的筹码，区别于直接读取当日筹码价档；也不等于总收益波动率。 原文：[破解处置效应：基于前景理论的筹码四阶矩因子构建与量化实证](https://zhuanlan.zhihu.com/p/2084953142454764201)。'
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
