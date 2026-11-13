"""demeaned_book_price_prospect_value_21d。

b_s=1/stock_day.pb[s]; x=SortAsc(b-M21(b),last21days); v(x)=x^0.88 if x>=0 else -2.25*(-x)^0.88; w_g(p)=p^g/(p^g+(1-p)^g)^(1/g); F=Sum(v(x_j)*(w_0.69(j/21)-w_0.69((j-1)/21)),x_j<0)+Sum(v(x_j)*(w_0.61((22-j)/21)-w_0.61((21-j)/21)),x_j>=0)
在账面市值比的历史偏离上应用损失厌恶与非线性概率权重，研究投资者对估值变化的非对称感知。 原文：[大年初一捅了个篓子，差点玷污了老外的名声！](https://zhuanlan.zhihu.com/p/2007862447000801689)。
沿作者修订代码先取BP再减窗口均值，而非直接对PB水平使用前景函数；v和w参数沿其所引用原前景价值文章的公开0.88、2.25、0.61、0.69。21日PB须完整且非0，窗口BP均值非0，不将负PB直接解释成低估；正负排序权重按修订后1起始索引展开，与先前收益前景价值输入不同。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'pb': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pb')}
FORMULA = 'b_s=1/stock_day.pb[s]; x=SortAsc(b-M21(b),last21days); v(x)=x^0.88 if x>=0 else -2.25*(-x)^0.88; w_g(p)=p^g/(p^g+(1-p)^g)^(1/g); F=Sum(v(x_j)*(w_0.69(j/21)-w_0.69((j-1)/21)),x_j<0)+Sum(v(x_j)*(w_0.61((22-j)/21)-w_0.61((21-j)/21)),x_j>=0)'
RECIPE = {'family': 'prospect', 'variant': 'book'}

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
    x = div(1, v['pb']) - rolling(div(1, v['pb']), 21)
    return x.rolling(21, min_periods=21).apply(prospect_value, raw=True) * 1

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
@fixed_factor('demeaned_book_price_prospect_value_21d', {})
class Factor_demeaned_book_price_prospect_value_21d(BaseFactor):
    name = 'demeaned_book_price_prospect_value_21d'
    description = '在账面市值比的历史偏离上应用损失厌恶与非线性概率权重，研究投资者对估值变化的非对称感知。 原文：[大年初一捅了个篓子，差点玷污了老外的名声！](https://zhuanlan.zhihu.com/p/2007862447000801689)。'
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
