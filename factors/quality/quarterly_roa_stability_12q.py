"""quarterly_roa_stability_12q。

N=Q(financial_income.n_income_attr_p); B=PITQ(financial_balance_sheet.total_assets); A=N/abs(B); A=NaN if (N<0 and B<0) or B=0; F=-Std(A_q,...,A_(q-11),ddof=1); minimum 8 valid quarters in last 12, latest required
以连续财报季度的归母资产收益率波动衡量盈利可持续性，降低一次性高盈利对质量评价的误导；不对日频前向填充值求波动。 原文：[精华贴分享｜【研报复现】财务质量类因子改进](https://zhuanlan.zhihu.com/p/2047701751445317203)。
实现纠正：恢复原报告约定的12季窗、至少8个有效季且最新季有效；ROA资产须正，ROE保留原负净资产约定，ddof=1。不对前向填充值求时序标准差。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_income__n_income_attr_p': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'n_income_attr_p', date_column='ann_date', expression='n_income_attr_p', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column='ann_date', expression='total_assets', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),))}
FORMULA = 'N=Q(financial_income.n_income_attr_p); B=PITQ(financial_balance_sheet.total_assets); A=N/abs(B); A=NaN if (N<0 and B<0) or B=0; F=-Std(A_q,...,A_(q-11),ddof=1); minimum 8 valid quarters in last 12, latest required'
RECIPE = {'family': 'quarterly_stability', 'terms': [['n', 'financial_income', 'n_income_attr_p', 'Q', 1], ['b', 'financial_balance_sheet', 'total_assets', 'B', 1]], 'quarters': 12, 'mode': 'Q', 'min_quarters': 8}

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
    x = [div(get('n', i), abs(get('b', i))).mask((get('n', i) < 0) & (get('b', i) < 0)) for i in range(12)]
    if fields['b'][1] == 'total_assets':
        x = [a.where(get('b', i) > 0) for (i, a) in enumerate(x)]
    array = np.stack([a.to_numpy(float) for a in x])
    count = np.isfinite(array).sum(axis=0)
    mean_value = div(np.nansum(array, axis=0), count)
    variance = div(np.nansum((array - mean_value) ** 2, axis=0), count - 1)
    return pd.DataFrame(-np.sqrt(variance), index=x[0].index, columns=x[0].columns).where(count >= 8).where(x[0].notna())

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
@fixed_factor('quarterly_roa_stability_12q', {})
class Factor_quarterly_roa_stability_12q(BaseFactor):
    name = 'quarterly_roa_stability_12q'
    description = '以连续财报季度的归母资产收益率波动衡量盈利可持续性，降低一次性高盈利对质量评价的误导；不对日频前向填充值求波动。 原文：[精华贴分享｜【研报复现】财务质量类因子改进](https://zhuanlan.zhihu.com/p/2047701751445317203)。'
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
