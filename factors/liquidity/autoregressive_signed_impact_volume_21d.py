"""autoregressive_signed_impact_volume_21d。

r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; X=sign(r)*(100*stock_day.vol); F=coefficient_of_X(OLS(r~1+L1(r)+X,last21tradingdays))
在收益自身短期延续的控制下，估计方向性成交股数对应的价格冲击，区分成交冲击与收益自相关。 原文：[增强非流动性因子，居然真的比非流动性因子强！](https://zhuanlan.zhihu.com/p/1994532903800046322)。
按正文“当日收益、前一日收益、一个月回归”明确使用日频数据，区别于无滞后收益控制的整窗分钟冲击回归。21日窗口至少18有效配对且设计矩阵满秩，股数、元、换手小数单位明确；股本变化已由每日turnover_rate体现，不把单位改变当作新增股数版。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol')}
FORMULA = 'r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; X=sign(r)*(100*stock_day.vol); F=coefficient_of_X(OLS(r~1+L1(r)+X,last21tradingdays))'
RECIPE = {'family': 'autoregressive_impact', 'field': 'vol', 'scale': 100}

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

def window_ols(y, xs, n, kind='last_residual', coefficient=-1, ridge=0, minimum=None):
    """完整窗口OLS。常数/共线解释量不以伪逆制造不唯一系数。"""
    out = y * np.nan
    for j in range(y.shape[1]):
        yy = y.iloc[:, j].to_numpy(float)
        xx = np.column_stack([x.iloc[:, j].to_numpy(float) for x in xs])
        for i in range(n - 1, len(y)):
            (a, b) = (yy[i - n + 1:i + 1], xx[i - n + 1:i + 1])
            valid = np.isfinite(a) & np.isfinite(b).all(axis=1)
            if valid.sum() < (n if minimum is None else minimum) or not valid[-1]:
                continue
            (a, b) = (a[valid], b[valid])
            design = np.column_stack([np.ones(len(a)), b])
            if np.linalg.matrix_rank(design) < design.shape[1] and ridge == 0:
                continue
            if ridge:
                penalty = np.eye(design.shape[1]) * ridge
                penalty[0, 0] = 0
                beta = np.linalg.solve(design.T @ design + penalty, design.T @ a)
            else:
                beta = np.linalg.lstsq(design, a, rcond=None)[0]
            e = a - design @ beta
            if kind == 'coef':
                v = beta[coefficient]
            elif kind == 'std':
                v = e.std(ddof=0)
            elif kind == 'fitted':
                v = (design @ beta)[-1]
            else:
                v = e[-1]
            out.iat[i, j] = v
    return out

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    x = v[recipe['field']] * recipe['scale']
    return window_ols(r, [r.shift(1), np.sign(r) * x], 21, 'coef', minimum=18)

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
@fixed_factor('autoregressive_signed_impact_volume_21d', {})
class Factor_autoregressive_signed_impact_volume_21d(BaseFactor):
    name = 'autoregressive_signed_impact_volume_21d'
    description = '在收益自身短期延续的控制下，估计方向性成交股数对应的价格冲击，区分成交冲击与收益自相关。 原文：[增强非流动性因子，居然真的比非流动性因子强！](https://zhuanlan.zhihu.com/p/1994532903800046322)。'
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
