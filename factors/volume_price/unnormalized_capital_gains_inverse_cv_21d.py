"""unnormalized_capital_gains_inverse_cv_21d。

u_s=stock_day.turnover_rate[s]/100; w_s=u_s*Prod(1-u_k,k=s+1..d); C=stock_day.close_hfq; X_d=1-Sum(w_s*C_s,s=d-20..d)/C_d; F=M21(X)/SD21(X)
按作者明确取k=1的残存交易权重构造历史成本，研究未归一化成本偏离水平相对波动的稳定程度。 原文：[自己瞎研究的因子（八）：资本利得突出量的变异系数，分层回测有一点点惊喜](https://zhuanlan.zhihu.com/p/699842817)。
来源代码明确不将权重和归一为1，故不擅改为现有标准CGO的归一权重；与已实现长窗归一CGO为不同构造。u必须已知且0<=u<=1，否则该窗口缺失，不把超过100%换手硬裁成概率。每个日X需21日真实完整量价，最终21日X完整需要41日输入，SD样本且正。CV来源未再次展开分母，少量歧义补为均值/标准差，并准确命名inverse_cv。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'turnover_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate'), 'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq')}
FORMULA = 'u_s=stock_day.turnover_rate[s]/100; w_s=u_s*Prod(1-u_k,k=s+1..d); C=stock_day.close_hfq; X_d=1-Sum(w_s*C_s,s=d-20..d)/C_d; F=M21(X)/SD21(X)'
RECIPE = {'family': 'capital_gains', 'variant': 'inverse_cv'}

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

def rolling(x, n, method='mean', ddof=0):
    n = int(n)
    if n < 1:
        raise ValueError('滚动窗口必须为正整数')
    roll = x.rolling(n, min_periods=n)
    if method in ('std', 'var'):
        return getattr(roll, method)(ddof=ddof)
    return getattr(roll, method)()

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    window = 21
    p = c
    u = v['turnover_rate'] / 100
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
            out.iat[t, j] = 1 - np.sum(w * price) / pp[t]
            continue
    return div(rolling(out, 21), rolling(out, 21, 'std'))

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
@fixed_factor('unnormalized_capital_gains_inverse_cv_21d', {})
class Factor_unnormalized_capital_gains_inverse_cv_21d(BaseFactor):
    name = 'unnormalized_capital_gains_inverse_cv_21d'
    description = '按作者明确取k=1的残存交易权重构造历史成本，研究未归一化成本偏离水平相对波动的稳定程度。 原文：[自己瞎研究的因子（八）：资本利得突出量的变异系数，分层回测有一点点惊喜](https://zhuanlan.zhihu.com/p/699842817)。'
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
