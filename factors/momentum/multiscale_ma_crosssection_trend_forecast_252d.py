"""multiscale_ma_crosssection_trend_forecast_252d。

Lset={3,5,10,20,50,100,200,400,600,800,1000}; X_i,t,L=Mean_last_L_trading_days(close_hfq_i)/close_hfq_i,t; R_i,s=close_hfq_i,s/close_hfq_i,s-21-1; beta_s=OLS_Coef(R_i,s ~ 1+X_i,s-21,L,across stocks); b_L,t=Mean(beta_s,L,s=t-251..t); F_i,t=Sum(b_L,t*X_i,t,L,L in Lset); MA_n uses last n trading days with minimum min(n,252) known prices
以历史截面回归估计不同期限均线对收益的贡献，再组合成股票预期收益，动态综合短期和长期价格趋势；只计综合预测，不把11个均线窗口重复计数。 原文：[美股上一个跨越时间尺度的趋势因子](https://zhuanlan.zhihu.com/p/51043407)。
本地覆盖修订：各均线仍为3、5、10、20、50、100、200、400、600、800、1000交易日观测窗，长均线至少252个有效价格；252日系数滚动均值及已实现21日训练收益保持原定义，不再强制新入池股票拥有1000个有效价格。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq')}
FORMULA = 'Lset={3,5,10,20,50,100,200,400,600,800,1000}; X_i,t,L=Mean_last_L_trading_days(close_hfq_i)/close_hfq_i,t; R_i,s=close_hfq_i,s/close_hfq_i,s-21-1; beta_s=OLS_Coef(R_i,s ~ 1+X_i,s-21,L,across stocks); b_L,t=Mean(beta_s,L,s=t-251..t); F_i,t=Sum(b_L,t*X_i,t,L,L in Lset); MA_n uses last n trading days with minimum min(n,252) known prices'
RECIPE = {'family': 'multiscale_ma'}

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
    windows = [3, 5, 10, 20, 50, 100, 200, 400, 600, 800, 1000]
    xs = [div(c.rolling(n, min_periods=min(n, 252)).mean(), c) for n in windows]
    betas = []
    out = c * np.nan
    for t in range(21, len(c)):
        y = div(c.iloc[t], c.iloc[t - 21]) - 1
        a = np.column_stack([np.ones(c.shape[1]), *[x.iloc[t - 21].to_numpy() for x in xs]])
        good = e.iloc[t].to_numpy() & np.isfinite(y.to_numpy()) & np.isfinite(a).all(axis=1)
        b = np.full(11, np.nan)
        if good.sum() >= 100 and np.linalg.matrix_rank(a[good]) == 12:
            b = np.linalg.lstsq(a[good], y.to_numpy()[good], rcond=None)[0][1:]
        betas.append(b)
        if len(betas) >= 252 and np.isfinite(betas[-252:]).all():
            out.iloc[t] = np.column_stack([x.iloc[t] for x in xs]) @ np.mean(betas[-252:], axis=0)
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
@fixed_factor('multiscale_ma_crosssection_trend_forecast_252d', {})
class Factor_multiscale_ma_crosssection_trend_forecast_252d(BaseFactor):
    name = 'multiscale_ma_crosssection_trend_forecast_252d'
    description = '以历史截面回归估计不同期限均线对收益的贡献，再组合成股票预期收益，动态综合短期和长期价格趋势；只计综合预测，不把11个均线窗口重复计数。 原文：[美股上一个跨越时间尺度的趋势因子](https://zhuanlan.zhihu.com/p/51043407)。'
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
