"""corrected_illiquidity_covariation_turnover_21d。

r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; V=stock_day.turnover_rate/100; B=OLS_slope(abs(r)~1+V,last21days); CV=SD21(V)/M21(V); F=M21(abs(r)/V)-B*CV
从平均交易冲击中扣除绝对收益对流通换手的斜率与规模变异的交互项，研究量价共同变化对简单冲击比率的修正。 原文：[非流动性因子改得这么复杂，效果真的会好吗？](https://zhuanlan.zhihu.com/p/1991174524197155352)。
采用来源明确尝试的21日均值非流动性−b×CV形式，不同时枚举当前日版本。所有21日r、V须完整，V及其均值正、V方差正；SD样本口径。公式是来源给出的代数修正，并不宣称该扣除项与第一项相同量纲或必然改善定价；不擅自更改CV定义使其“看起来更合理”。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'), 'turnover_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate')}
FORMULA = 'r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; V=stock_day.turnover_rate/100; B=OLS_slope(abs(r)~1+V,last21days); CV=SD21(V)/M21(V); F=M21(abs(r)/V)-B*CV'
RECIPE = {'family': 'corrected_illiquidity', 'field': 'turnover_rate', 'scale': 0.01}

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

def pair_rolling(a, b, n, method='corr', ddof=0):
    valid = np.isfinite(a) & np.isfinite(b)
    (aa, bb) = (a.where(valid), b.where(valid))
    if method == 'corr':
        result = aa.rolling(int(n), min_periods=int(n)).corr(bb)
        return result.where(rolling(aa, n, 'var') > 0).where(rolling(bb, n, 'var') > 0)
    return aa.rolling(int(n), min_periods=int(n)).cov(bb, ddof=ddof)

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    x = v[recipe['field']] * recipe['scale']
    beta = div(pair_rolling(abs(r), x, 21, 'cov'), rolling(x, 21, 'var'))
    return rolling(div(abs(r), x), 21) - beta * div(rolling(x, 21, 'std'), rolling(x, 21))

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
@fixed_factor('corrected_illiquidity_covariation_turnover_21d', {})
class Factor_corrected_illiquidity_covariation_turnover_21d(BaseFactor):
    name = 'corrected_illiquidity_covariation_turnover_21d'
    description = '从平均交易冲击中扣除绝对收益对流通换手的斜率与规模变异的交互项，研究量价共同变化对简单冲击比率的修正。 原文：[非流动性因子改得这么复杂，效果真的会好吗？](https://zhuanlan.zhihu.com/p/1991174524197155352)。'
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
