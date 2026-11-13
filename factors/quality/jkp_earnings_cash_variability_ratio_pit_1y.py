"""jkp_earnings_cash_variability_ratio_pit_1y。

N_y=Y(financial_income.n_income)/LagFY(Y(financial_balance_sheet.total_assets),1); C_y=Y(financial_cash_flow.n_cashflow_act)/LagFY(Y(financial_balance_sheet.total_assets),1); F=Std(N_y,...,N_(y-4),ddof=1)/Std(C_y,...,C_(y-4),ddof=1); use paired valid annual ratios within five-year window, minimum 2, latest pair required
比较资产标准化利润与现金流的多年波动，衡量利润相对现金流是否被平滑；比值低不自动代表高质量，须结合会计确认理解。 原文：[JKP公开研究因子定义：earnings_variability](https://github.com/bkelly-lab/jkp-data/blob/main/src/jkp/data/aux_functions.py)。
本地覆盖修订：五年观测窗内仅使用利润、现金流及上年资产都可见的配对年度，至少2对且最新年度有效，样本标准差；不把缺失科目补零、不跳改报告年的滞后。此为不完整历史估计版。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_balance_sheet__total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column='ann_date', expression='total_assets', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_cash_flow__n_cashflow_act': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_cashflow_act', date_column='ann_date', expression='n_cashflow_act', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__n_income': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'n_income', date_column='ann_date', expression='n_income', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),))}
FORMULA = 'N_y=Y(financial_income.n_income)/LagFY(Y(financial_balance_sheet.total_assets),1); C_y=Y(financial_cash_flow.n_cashflow_act)/LagFY(Y(financial_balance_sheet.total_assets),1); F=Std(N_y,...,N_(y-4),ddof=1)/Std(C_y,...,C_(y-4),ddof=1); use paired valid annual ratios within five-year window, minimum 2, latest pair required'
RECIPE = {'family': 'financial_history', 'variant': 'variability_ratio', 'terms': [['n', 'financial_income', 'n_income', 'Y', 4], ['c', 'financial_cash_flow', 'n_cashflow_act', 'Y', 4], ['a', 'financial_balance_sheet', 'total_assets', 'Y', 4]], 'quarters': 6, 'min_observations': 2}

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
    n = [div(get('n', i), positive(get('a', i + 1))) for i in range(5)]
    c = [div(get('c', i), positive(get('a', i + 1))) for i in range(5)]
    paired = np.stack([np.isfinite(a.to_numpy()) & np.isfinite(b.to_numpy()) for (a, b) in zip(n, c)])

    def partial_sd(xs):
        a = np.where(paired, np.stack([x.to_numpy(float) for x in xs]), np.nan)
        known = paired.sum(axis=0)
        mu = div(np.nansum(a, axis=0), known)
        var = div(np.nansum((a - mu) ** 2, axis=0), known - 1)
        return pd.DataFrame(np.sqrt(var), index=xs[0].index, columns=xs[0].columns).where(known >= recipe.get('min_observations', 3)).where(paired[0])
    return div(partial_sd(n), partial_sd(c))

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
@fixed_factor('jkp_earnings_cash_variability_ratio_pit_1y', {})
class Factor_jkp_earnings_cash_variability_ratio_pit_1y(BaseFactor):
    name = 'jkp_earnings_cash_variability_ratio_pit_1y'
    description = '比较资产标准化利润与现金流的多年波动，衡量利润相对现金流是否被平滑；比值低不自动代表高质量，须结合会计确认理解。 原文：[JKP公开研究因子定义：earnings_variability](https://github.com/bkelly-lab/jkp-data/blob/main/src/jkp/data/aux_functions.py)。'
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
