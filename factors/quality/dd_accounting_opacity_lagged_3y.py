"""dd_accounting_opacity_lagged_3y。

WC_y=AnnualPIT(accounts_receiv+inventories-acct_payable-taxes_payable+oth_cur_assets); A=LagFY(total_assets,1); e_y=OLSResidual_no_intercept((WC_y-WC_(y-1))/A ~ 1/A+C_(y-1)/A+C_y/A); F=-Mean(abs(e_y),abs(e_(y-1)),abs(e_(y-2)),known only), latest e_y required
用当期及滞后经营现金流解释营运资本应计，再平均最近三年内已可见的残差绝对值，度量会计信息不透明程度；偏好误差较小者。 原文：[DD模型(Dechow and Dichev,2002)理论推导和stata实现](https://zhuanlan.zhihu.com/p/648504599)。
本地定义修订：采用仅含当期与滞后经营现金流的DD启发式因果版本，删除需要未来年度现金流的解释项；三年窗至少最新1个已可见残差，按有效残差均值而非三项硬求和。行业样本不足20家时回退同报告年非金融池；不再声称严格复现原DD模型。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_balance_sheet__accounts_receiv': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'accounts_receiv', date_column='ann_date', expression='accounts_receiv', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__inventories': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'inventories', date_column='ann_date', expression='inventories', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__acct_payable': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'acct_payable', date_column='ann_date', expression='acct_payable', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__taxes_payable': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'taxes_payable', date_column='ann_date', expression='taxes_payable', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__oth_cur_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'oth_cur_assets', date_column='ann_date', expression='oth_cur_assets', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column='ann_date', expression='total_assets', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_cash_flow__n_cashflow_act': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_cashflow_act', date_column='ann_date', expression='n_cashflow_act', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1')}
FORMULA = 'WC_y=AnnualPIT(accounts_receiv+inventories-acct_payable-taxes_payable+oth_cur_assets); A=LagFY(total_assets,1); e_y=OLSResidual_no_intercept((WC_y-WC_(y-1))/A ~ 1/A+C_(y-1)/A+C_y/A); F=-Mean(abs(e_y),abs(e_(y-1)),abs(e_(y-2)),known only), latest e_y required'
RECIPE = {'family': 'dd_opacity', 'terms': [['a', 'financial_balance_sheet', 'total_assets', 'Y', 4], ['ar', 'financial_balance_sheet', 'accounts_receiv', 'Y', 4], ['inv', 'financial_balance_sheet', 'inventories', 'Y', 4], ['pay', 'financial_balance_sheet', 'acct_payable', 'Y', 4], ['tax', 'financial_balance_sheet', 'taxes_payable', 'Y', 4], ['other', 'financial_balance_sheet', 'oth_cur_assets', 'Y', 4], ['c', 'financial_cash_flow', 'n_cashflow_act', 'Y', 4]], 'quarters': 5, 'causal_cashflow': True}

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
    errors = []
    periods = (0, 1, 2)
    for i in periods:
        wc = lambda k: get('ar', k) + get('inv', k) - get('pay', k) - get('tax', k) + get('other', k)
        base = positive(get('a', i + 1))
        controls = [div(1, base), div(get('c', i + 1), base), div(get('c', i), base)]
        e = financial_regression(div(wc(i) - wc(i + 1), base), controls, year - i, industry, eligible)
        errors.append(e)
    a = np.stack([abs(e).to_numpy() for e in errors])
    count = np.isfinite(a).sum(axis=0)
    return pd.DataFrame(-div(np.nansum(a, axis=0), count), index=errors[0].index, columns=errors[0].columns).where(errors[0].notna())

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
@fixed_factor('dd_accounting_opacity_lagged_3y', {})
class Factor_dd_accounting_opacity_lagged_3y(BaseFactor):
    name = 'dd_accounting_opacity_lagged_3y'
    description = '用当期及滞后经营现金流解释营运资本应计，再平均最近三年内已可见的残差绝对值，度量会计信息不透明程度；偏好误差较小者。 原文：[DD模型(Dechow and Dichev,2002)理论推导和stata实现](https://zhuanlan.zhihu.com/p/648504599)。'
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
