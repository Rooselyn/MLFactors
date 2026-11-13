"""barra_local_sales_per_share_normalized_trend_5y。

X_k=AnnualPIT(financial_income.revenue/financial_balance_sheet.total_share)_(y-k),k=0..4; F=OLS_slope(X~1+actual_year)/abs(Mean(X)); minimum 3 known years and latest known
以五个完整年度的每股营业收入拟合稳定线性变化并按水平归一，比较长期趋势而非只比较首尾两个点。 原文：[知乎BARRA CNE6模型复现引用的公开源码](https://github.com/ShiliangZhang-nku/Barra_CNE6/blob/master/barra_cne6_factor.py)。
本地覆盖修订：五年窗至少3个有效年、最新年有效；按真实年份坐标拟合，股数使用财报total_share且须正，缺年不插值，均值为0缺失。跨表采用共同最新已公告年度。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_balance_sheet__total_share': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_share', date_column='ann_date', expression='total_share', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column='ann_date', expression='revenue', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),))}
FORMULA = 'X_k=AnnualPIT(financial_income.revenue/financial_balance_sheet.total_share)_(y-k),k=0..4; F=OLS_slope(X~1+actual_year)/abs(Mean(X)); minimum 3 known years and latest known'
RECIPE = {'family': 'financial_history', 'variant': 'positive_trend', 'per_share': True, 'terms': [['sales', 'financial_income', 'revenue', 'Y', 4], ['shares', 'financial_balance_sheet', 'total_share', 'Y', 4]], 'quarters': 5}

class FinancialContext:

    def __init__(self, inputs, dates, symbols, reports=None):
        self.inputs = inputs
        self.dates = dates
        self.symbols = symbols
        self.reports = reports if reports is not None else _formula_calculations.read_reports({k: v for (k, v) in inputs.items() if 'financial_' in v.path}, end=dates.max(), symbols=list(symbols))

    def panels(self, leaves, annual=False):
        return _formula_calculations.leaf_panels({'leaves': leaves, 'annual': annual}, self.reports, self.dates, self.symbols, return_available=True)

    def history(self, terms, n, mode='Y'):
        leaves = {f'{key}_{i}': (table, field, m, step * i) for (key, (table, field, m, step)) in terms.items() for i in range(n)}
        (env, self.available) = self.panels(leaves, mode == 'Y')
        return {key: [env[f'{key}_{i}'] for i in range(n)] for key in terms}

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

def compute_financial(recipe, context, values, eligible):
    family = recipe['family']
    variant = recipe.get('variant', '')
    fields = {k: (t, f, m, s) for (k, t, f, m, s) in recipe.get('terms', [])}
    h = context.history(fields, recipe.get('quarters', 1), recipe.get('mode', 'Y'))

    def get(k, i=0):
        return h[k][i]

    def positive(x):
        return x.where(x > 0)

    def mean(a):
        return sum(a) / len(a)

    def sd(a, ddof=1):
        m = mean(a)
        return np.sqrt(sum(((x - m) ** 2 for x in a)) / (len(a) - ddof))
    x = [div(get('sales', i), positive(get('shares', i))) for i in range(recipe['quarters'])]
    arrays = np.stack([a.to_numpy(float) for a in x])
    valid = np.isfinite(arrays)
    count = valid.sum(axis=0)
    average = div(np.nansum(arrays, axis=0), count)
    allowed = (count >= 3) & valid[0]
    wrap = lambda a: pd.DataFrame(a, index=x[0].index, columns=x[0].columns).where(allowed)
    t = np.arange(len(x), 0, -1, dtype=float)[:, None, None]
    center = div(np.sum(np.where(valid, t, 0), axis=0), count)
    slope = div(np.nansum((t - center) * (arrays - average), axis=0), np.sum(np.where(valid, (t - center) ** 2, 0), axis=0))
    return wrap(div(slope, abs(average)) * 1)

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
@fixed_factor('barra_local_sales_per_share_normalized_trend_5y', {})
class Factor_barra_local_sales_per_share_normalized_trend_5y(BaseFactor):
    name = 'barra_local_sales_per_share_normalized_trend_5y'
    description = '以五个完整年度的每股营业收入拟合稳定线性变化并按水平归一，比较长期趋势而非只比较首尾两个点。 原文：[知乎BARRA CNE6模型复现引用的公开源码](https://github.com/ShiliangZhang-nku/Barra_CNE6/blob/master/barra_cne6_factor.py)。'
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
            context = FinancialContext(self.INPUTS, dates, symbols)
            value = compute_financial(recipe, context, v, e)
            if hasattr(context, 'available'):
                self.available_ann_dates = context.available
        return finite(value).astype(float).where(e).rename_axis(index='date', columns='symbol')
