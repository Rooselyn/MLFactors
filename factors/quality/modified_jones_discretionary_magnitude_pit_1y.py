"""modified_jones_discretionary_magnitude_pit_1y。

Y=AnnualPIT; A=LagFY(Y(financial_balance_sheet.total_assets),1); T=(Y(financial_income.n_income)-Y(financial_cash_flow.n_cashflow_act))/A; X1=1/A; X2=DeltaFY(Y(financial_income.revenue))/A; X3=Y(financial_balance_sheet.fix_assets)/A; beta=OLS_no_intercept(T~X1+X2+X3,within industry_sw_1); NDA=beta1/A+beta2*(DeltaFY(Y(financial_income.revenue))-DeltaFY(Y(financial_balance_sheet.accounts_receiv)))/A+beta3*X3; F=-abs(T-NDA); industry groups with fewer than 20 valid stocks use the same visible report-year nonfinancial pool
对无法被正常经营解释的应计项取绝对值，偏好异常应计程度较低的公司；原始回归用收入增量估系数，预测正常应计时再扣除应收增量，遵循修正Jones的两阶段口径。 原文：[应计盈余管理指标的计算——基于修正Jones模型的操纵性应计项目DA](https://zhuanlan.zhihu.com/p/695920794)。
本地覆盖修订：同行业、同报告年有效样本满20家时保留原分组回归，否则使用同一已可见报告年的非金融股票池回归；保持无截距、组内1%/99%缩尾、满秩检查和财报滞后。金融股及真实缺字段仍缺失。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_balance_sheet__total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column='ann_date', expression='total_assets', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__n_income': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'n_income', date_column='ann_date', expression='n_income', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_cash_flow__n_cashflow_act': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_cashflow_act', date_column='ann_date', expression='n_cashflow_act', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column='ann_date', expression='revenue', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__fix_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'fix_assets', date_column='ann_date', expression='fix_assets', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__accounts_receiv': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'accounts_receiv', date_column='ann_date', expression='accounts_receiv', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1')}
FORMULA = 'Y=AnnualPIT; A=LagFY(Y(financial_balance_sheet.total_assets),1); T=(Y(financial_income.n_income)-Y(financial_cash_flow.n_cashflow_act))/A; X1=1/A; X2=DeltaFY(Y(financial_income.revenue))/A; X3=Y(financial_balance_sheet.fix_assets)/A; beta=OLS_no_intercept(T~X1+X2+X3,within industry_sw_1); NDA=beta1/A+beta2*(DeltaFY(Y(financial_income.revenue))-DeltaFY(Y(financial_balance_sheet.accounts_receiv)))/A+beta3*X3; F=-abs(T-NDA); industry groups with fewer than 20 valid stocks use the same visible report-year nonfinancial pool'
RECIPE = {'family': 'jones', 'variant': 'magnitude', 'terms': [['a', 'financial_balance_sheet', 'total_assets', 'Y', 4], ['n', 'financial_income', 'n_income', 'Y', 4], ['c', 'financial_cash_flow', 'n_cashflow_act', 'Y', 4], ['s', 'financial_income', 'revenue', 'Y', 4], ['fix', 'financial_balance_sheet', 'fix_assets', 'Y', 4], ['ar', 'financial_balance_sheet', 'accounts_receiv', 'Y', 4]], 'quarters': 2}

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

def financial_regression(y, xs, year, industry, eligible, minimum=20, fitted_xs=None):
    """同信号日、同报告年、同行业回归；金融业和非满秩组留缺失。"""
    out = y * np.nan
    for d in y.index:
        group = industry.loc[d].astype('string')
        valid = eligible.loc[d] & group.notna() & ~group.str.contains('银行|非银|金融', na=True)
        frame = pd.DataFrame({'y': y.loc[d], 'year': year.loc[d], 'industry': group})
        for (i, x) in enumerate(xs):
            frame[f'x{i}'] = x.loc[d]
        if fitted_xs:
            for (i, x) in enumerate(fitted_xs):
                frame[f'f{i}'] = x.loc[d]
        frame = frame.loc[valid].replace([np.inf, -np.inf], np.nan).dropna()
        for ((report_year, _), g) in frame.groupby(['year', 'industry'], sort=False):
            training = g if len(g) >= minimum else frame.loc[frame.year.eq(report_year)]
            if len(training) < minimum:
                continue
            fit = training[[f'x{i}' for i in range(len(xs))]].copy()
            (lo, hi) = (fit.quantile(0.01), fit.quantile(0.99))
            fit = fit.clip(lo, hi, axis=1)
            a = fit.to_numpy(float)
            b = training.y.to_numpy(float)
            if np.linalg.matrix_rank(a) < a.shape[1]:
                continue
            beta = np.linalg.lstsq(a, b, rcond=None)[0]
            test = g[[f'f{i}' for i in range(len(xs))]].copy() if fitted_xs else g[[f'x{i}' for i in range(len(xs))]].copy()
            test.columns = fit.columns
            test = test.clip(lo, hi, axis=1)
            prediction = test.to_numpy(float) @ beta
            out.loc[d, g.index] = prediction if fitted_xs else g.y.to_numpy(float) - prediction
    return out

def report_year_panel(context):
    reports = {}
    leaves = {}
    for (i, (table, frame)) in enumerate(context.reports.items()):
        a = frame.copy()
        a['_report_year'] = a['_period'] // 4
        a['_report_period'] = a['_period']
        reports[table] = a
        leaves['year_' + str(i)] = (table, '_report_year', 'Y', 0)
    env = _formula_calculations.leaf_panels({'leaves': leaves, 'annual': True}, reports, context.dates, context.symbols)
    return next(iter(env.values()))

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
    year = report_year_panel(context)
    industry = values['industry_sw_1']
    a = positive(get('a', 1))
    inv = div(1, a)
    t = div(get('n') - get('c'), a)
    ds = div(get('s') - get('s', 1), a)
    fix = div(get('fix'), a)
    nda = financial_regression(t, [inv, ds, fix], year, industry, eligible, fitted_xs=[inv, div(get('s') - get('s', 1) - get('ar') + get('ar', 1), a), fix])
    return -abs(t - nda)

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
@fixed_factor('modified_jones_discretionary_magnitude_pit_1y', {})
class Factor_modified_jones_discretionary_magnitude_pit_1y(BaseFactor):
    name = 'modified_jones_discretionary_magnitude_pit_1y'
    description = '对无法被正常经营解释的应计项取绝对值，偏好异常应计程度较低的公司；原始回归用收入增量估系数，预测正常应计时再扣除应收增量，遵循修正Jones的两阶段口径。 原文：[应计盈余管理指标的计算——基于修正Jones模型的操纵性应计项目DA](https://zhuanlan.zhihu.com/p/695920794)。'
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
