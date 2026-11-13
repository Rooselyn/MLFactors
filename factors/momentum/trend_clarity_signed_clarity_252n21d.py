"""trend_clarity_signed_clarity_252n21d。

P=stock_day.close_hfq with stock_day.vol>0; W=t-251..t-21; TC=R_squared(OLS(P_s~1+s,s in W)); MOM=Sum(stock_day.close_hfq[s]/stock_day.close_hfq[s-1]-1,s in W); F=TC*sign(MOM)
用长期线性价格路径的拟合优度衡量按既有趋势方向赋号的价格路径清晰度，研究趋势明确时价格运动的延续性。 原文：[趋势清晰动量因子，大A对动量的研究可以说是“子子孙孙无穷尽也”！](https://zhuanlan.zhihu.com/p/2044531475710736328)。
按公开231日收益和与价格回归窗口统一为排除最近21日的231个交易日；固定使用交易日序号回归，有效价格至少200、价格方差正。停牌量零记价格缺失、收益需相邻两日有效，不按默认pct_change向前填充；本地要求窗口收益全231项有效，否则缺失，避免缺日宽松求和。源代码循环和输出日期切片明显不一致，报告以公式窗口及信号日对齐，不照搬样本起点硬编码。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol')}
FORMULA = 'P=stock_day.close_hfq with stock_day.vol>0; W=t-251..t-21; TC=R_squared(OLS(P_s~1+s,s in W)); MOM=Sum(stock_day.close_hfq[s]/stock_day.close_hfq[s-1]-1,s in W); F=TC*sign(MOM)'
RECIPE = {'family': 'clarity', 'variant': 'signed'}

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

def trend(x, n, kind='slope', tiny=0):
    n = int(n)
    t = np.arange(1, n + 1, dtype=float)
    tc = t - t.mean()
    den = tc @ tc
    if den == 0:
        return x * np.nan
    mean = rolling(x, n)
    slope = x.rolling(n, min_periods=n).apply(lambda a: a @ tc / den, raw=True)
    if kind == 'slope':
        return slope
    if kind == 'resi':
        return x - mean - slope * tc[-1]
    return div(slope.pow(2) * den, rolling(x, n, 'var') * n).where(rolling(x, n, 'std') > tiny)

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    price = c.where(v['vol'] > 0).shift(21)
    tc = trend(price, 231, 'r2')
    mom = rolling(r.shift(21), 231, 'sum')
    return tc * np.sign(mom)

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
@fixed_factor('trend_clarity_signed_clarity_252n21d', {})
class Factor_trend_clarity_signed_clarity_252n21d(BaseFactor):
    name = 'trend_clarity_signed_clarity_252n21d'
    description = '用长期线性价格路径的拟合优度衡量按既有趋势方向赋号的价格路径清晰度，研究趋势明确时价格运动的延续性。 原文：[趋势清晰动量因子，大A对动量的研究可以说是“子子孙孙无穷尽也”！](https://zhuanlan.zhihu.com/p/2044531475710736328)。'
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
