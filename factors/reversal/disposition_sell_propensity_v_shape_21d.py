"""disposition_sell_propensity_v_shape_21d。

W=10*stock_day.amount/stock_day.vol*stock_day.adj_factor; u=stock_day.turnover_rate/100; a_s=u_s*Prod(1-u_j,j=s+1..t-1),s=t-20..t-1; w_s=a_s/Sum(a_s); x_s=W_t/W_s-1; G=Sum(w_s*max(x_s,0)); L=Sum(w_s*min(x_s,0)); S=G-3*L; F=S
用历史换手衰减近似持仓成本权重，研究以亏损部分三倍敏感度估算的潜在卖出压力；不是实际账户持仓或真实卖单统计。 原文：[卖出倾向因子，行为金融学在大A能带来毁天灭地的效果嘛？](https://zhuanlan.zhihu.com/p/2058668940595815371)。
采用来源实际展示的亏损权重3，仅保留一个系数，不把1/1.25/1.5/2/3逐一计成新因子。源码含当前日21个VWAP，历史成本实际20天；上述乘积严格排除买入日自身生存因子，等价于原tr/(1-tr)*反向cumprod。turnover_rate百分数转小数并要求0<=u<1，历史量额价格完整且正、权重和正；不把大于100%的未知持仓周转随意裁成确定生存概率。VWAP手与千元换为元/股并各日复权。第二项是原文实际尝试的截面均值距离化，不增添未试过的中性化组合。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount'), 'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'), 'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor'), 'turnover_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate')}
FORMULA = 'W=10*stock_day.amount/stock_day.vol*stock_day.adj_factor; u=stock_day.turnover_rate/100; a_s=u_s*Prod(1-u_j,j=s+1..t-1),s=t-20..t-1; w_s=a_s/Sum(a_s); x_s=W_t/W_s-1; G=Sum(w_s*max(x_s,0)); L=Sum(w_s*min(x_s,0)); S=G-3*L; F=S'
RECIPE = {'family': 'disposition', 'variant': 'raw'}

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
    window = 21
    p = div(v['amount'] * 10, v['vol']) * v['adj_factor']
    u = v['turnover_rate'] / 100
    out = p * np.nan
    for j in range(p.shape[1]):
        (pp, uu) = (p.iloc[:, j].to_numpy(float), u.iloc[:, j].to_numpy(float))
        for t in range(window - 1, len(p)):
            price = pp[t - window + 1:t + 1]
            turn = uu[t - window + 1:t + 1]
            if not (np.isfinite(price).all() and np.isfinite(turn).all()) or np.any(price <= 0):
                continue
            (price, turn) = (price[:-1], turn[:-1])
            survive = np.r_[np.cumprod(1 - turn[:0:-1])[::-1], 1.0]
            w = turn * survive
            if w.sum() <= 0:
                continue
            w = w / w.sum()
            x = pp[t] / price - 1
            out.iat[t, j] = np.sum(w * np.maximum(x, 0)) - 3 * np.sum(w * np.minimum(x, 0))
            continue
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
@fixed_factor('disposition_sell_propensity_v_shape_21d', {})
class Factor_disposition_sell_propensity_v_shape_21d(BaseFactor):
    name = 'disposition_sell_propensity_v_shape_21d'
    description = '用历史换手衰减近似持仓成本权重，研究以亏损部分三倍敏感度估算的潜在卖出压力；不是实际账户持仓或真实卖单统计。 原文：[卖出倾向因子，行为金融学在大A能带来毁天灭地的效果嘛？](https://zhuanlan.zhihu.com/p/2058668940595815371)。'
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
