"""gain_loss_variance_structure_local_1d。

r=close_hfq/L1(close_hfq)-1; A=Var(r>0 values,last 120d,ddof=1)/Var(r<0 values,last 120d,ddof=1); B=Var(r>0 values,last 60d,ddof=1); F=-R(abs(A-B))
比较中期涨跌条件方差不对称与短期正收益方差，研究波动结构背离程度。保留源式不同量纲的直接相减，不擅自将其改成普通方差或额外标准化。 原文：[【实战因子365】58.方差比率背离因子（IC 0.0358，sharpe 1.4907）](https://zhuanlan.zhihu.com/p/2037592074220999156)。
基础指标按用户已实现JSON中GainLossVarianceRatio与GainVariance的明确本地定义展开，后者只含正收益，不采用文章正文误称整体方差。两个120日条件组至少各2条，60日正收益至少2条，负收益方差须正，窗口日收益完整；输出秩为原公共R。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq')}
FORMULA = 'r=close_hfq/L1(close_hfq)-1; A=Var(r>0 values,last 120d,ddof=1)/Var(r<0 values,last 120d,ddof=1); B=Var(r>0 values,last 60d,ddof=1); F=-R(abs(A-B))'
RECIPE = {'family': 'gain_loss_variance'}

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

def rank(x, mode='unit', minimum=1, eligible=None):
    x = finite(x)
    if eligible is not None:
        x = x.where(eligible)
    count = x.count(axis=1)
    r = x.rank(axis=1, method='average')
    if mode == 'unit':
        out = div(r.sub(1), count.sub(1).replace(0, np.nan).to_numpy()[:, None])
        out = out.mask(x.notna() & count.eq(1).to_numpy()[:, None], 0.5)
    else:
        out = r.div(count.replace(0, np.nan), axis=0)
    return out.where(count.ge(minimum), axis=0)

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None

    def varpart(x, n, up):
        return x.rolling(n, min_periods=n).apply(lambda a: np.var(a[a > 0] if up else a[a < 0], ddof=1) if np.sum(a > 0 if up else a < 0) >= 2 else np.nan, raw=True)
    a = div(varpart(r, 120, True), varpart(r, 120, False))
    b = varpart(r, 60, True)
    return -rank(abs(a - b), eligible=e)

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
@fixed_factor('gain_loss_variance_structure_local_1d', {})
class Factor_gain_loss_variance_structure_local_1d(BaseFactor):
    name = 'gain_loss_variance_structure_local_1d'
    description = '比较中期涨跌条件方差不对称与短期正收益方差，研究波动结构背离程度。保留源式不同量纲的直接相减，不擅自将其改成普通方差或额外标准化。 原文：[【实战因子365】58.方差比率背离因子（IC 0.0358，sharpe 1.4907）](https://zhuanlan.zhihu.com/p/2037592074220999156)。'
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
