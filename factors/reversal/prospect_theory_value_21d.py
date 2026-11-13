"""prospect_theory_value_21d。

R=SortAsc(close_hfq/L1(close_hfq)-1,last 21d); n=Count(R); v(x)=x^0.88 if x>=0 else -2.25*(-x)^0.88; w_g(p)=p^g/(p^g+(1-p)^g)^(1/g); TK=Sum(v(R_j)*(w_0.69(j/n)-w_0.69((j-1)/n)),R_j<0)+Sum(v(R_j)*(w_0.61((n-j+1)/n)-w_0.61((n-j)/n)),R_j>=0); F=-TK
通过损失厌恶及非线性概率加权衡量近期收益分布的主观吸引力，研究受偏好追捧后的低预期收益。不同于简单收益均值、偏度或最大收益。 原文：[前景价值，老外的因子能克服水土不服吗？](https://zhuanlan.zhihu.com/p/2007157465649784613)。
j为所有有效收益的1起始升序序号，n至少6。修正原文正收益循环的偏移错误，使累计概率始终在[0,1]且最高收益使用w(1/n)-w(0)；此为明确标注的边界修正，不沿用可能p>1的代码。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq')}
FORMULA = 'R=SortAsc(close_hfq/L1(close_hfq)-1,last 21d); n=Count(R); v(x)=x^0.88 if x>=0 else -2.25*(-x)^0.88; w_g(p)=p^g/(p^g+(1-p)^g)^(1/g); TK=Sum(v(R_j)*(w_0.69(j/n)-w_0.69((j-1)/n)),R_j<0)+Sum(v(R_j)*(w_0.61((n-j+1)/n)-w_0.61((n-j)/n)),R_j>=0); F=-TK'
RECIPE = {'family': 'prospect', 'variant': 'returns'}

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

def prospect_value(a):
    a = np.sort(a)
    n = len(a)
    j = np.arange(1, n + 1)

    def w(p, g):
        return p ** g / (p ** g + (1 - p) ** g) ** (1 / g)
    weights = np.where(a < 0, w(j / n, 0.69) - w((j - 1) / n, 0.69), w((n - j + 1) / n, 0.61) - w((n - j) / n, 0.61))
    val = np.where(a >= 0, abs(a) ** 0.88, -2.25 * abs(a) ** 0.88)
    return val @ weights

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    x = r
    return x.rolling(21, min_periods=21).apply(prospect_value, raw=True) * -1

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
@fixed_factor('prospect_theory_value_21d', {})
class Factor_prospect_theory_value_21d(BaseFactor):
    name = 'prospect_theory_value_21d'
    description = '通过损失厌恶及非线性概率加权衡量近期收益分布的主观吸引力，研究受偏好追捧后的低预期收益。不同于简单收益均值、偏度或最大收益。 原文：[前景价值，老外的因子能克服水土不服吗？](https://zhuanlan.zhihu.com/p/2007157465649784613)。'
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
