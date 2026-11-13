"""annual_ebo_valuation_deviation_1y。

B=AnnualPIT(financial_balance_sheet.total_hldr_eqy_inc_min_int); E=AnnualPIT(financial_income.n_income); Y=ln(10000*stock_day.total_mv); F=CSOLSResidual(Y~1+ln(B)+ln(E))
以当时已公布的年度账面权益和净利润解释市值，残差越大表示相对基本面回归估值更贵，研究市场价格偏离财务价值的程度。 原文：[一个比PE和PB更好的指标——估值偏离度](https://zhuanlan.zhihu.com/p/35103319)。
原文使用Total_Equity_Y和Net_Income_Y但未披露少数股东口径，本地明确用含少数股东的总权益和净利润配对，不混用。两表共同最新已知完整年报同一12月31日end_date，实际公告日优先、否则ann_date，下一交易日可用；禁止用未来修订覆盖历史。B、E、市值均正，截面至少100只、设计矩阵满秩。仅取回归残差，文中“最低50只”选股条件不纳入；与含行业、杠杆和滞后季度变量的特异规模模型为不同明确模型。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'financial_balance_sheet__total_hldr_eqy_inc_min_int': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_hldr_eqy_inc_min_int', date_column='ann_date', expression='total_hldr_eqy_inc_min_int', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__ann_date': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'ann_date', date_column='ann_date', expression='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__f_ann_date': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'f_ann_date', date_column='ann_date', expression='f_ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__end_date': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'end_date', date_column='ann_date', expression='end_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__n_income': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'n_income', date_column='ann_date', expression='n_income', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__ann_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'ann_date', date_column='ann_date', expression='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__f_ann_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'f_ann_date', date_column='ann_date', expression='f_ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__end_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'end_date', date_column='ann_date', expression='end_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),))}
FORMULA = 'B=AnnualPIT(financial_balance_sheet.total_hldr_eqy_inc_min_int); E=AnnualPIT(financial_income.n_income); Y=ln(10000*stock_day.total_mv); F=CSOLSResidual(Y~1+ln(B)+ln(E))'
RECIPE = {'family': 'annual_ebo', 'terms': [['b', 'financial_balance_sheet', 'total_hldr_eqy_inc_min_int', 'Y', 4], ['n', 'financial_income', 'n_income', 'Y', 4]], 'quarters': 1}

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

def cs_residual(y, *xs, intercept=True, minimum=None, return_fitted=False):
    out = y * np.nan
    for i in range(len(y)):
        target = y.iloc[i].to_numpy(float)
        xx = np.column_stack([x.iloc[i].to_numpy(float) for x in xs])
        valid = np.isfinite(target) & np.isfinite(xx).all(axis=1)
        if valid.sum() < (minimum or xx.shape[1] + int(intercept)):
            continue
        design = xx[valid]
        if intercept and design.shape[1] == 1 and (np.ptp(design[:, 0]) == 0):
            fitted = np.full(valid.sum(), target[valid].mean())
        else:
            if intercept:
                design = np.column_stack([np.ones(valid.sum()), design])
            if np.linalg.matrix_rank(design) < design.shape[1]:
                continue
            fitted = design @ np.linalg.lstsq(design, target[valid], rcond=None)[0]
        out.iloc[i, np.flatnonzero(valid)] = fitted if return_fitted else target[valid] - fitted
    return out

def log(x, base=np.e, offset=0):
    z = x + offset
    if isinstance(z, (pd.DataFrame, pd.Series)):
        z = z.where(z > 0)
    else:
        z = np.where(z > 0, z, np.nan)
    return np.log(z) / np.log(base)

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
    return cs_residual(log(values['total_mv'] * 10000).where(eligible), log(get('b')).where(eligible), log(get('n')).where(eligible), minimum=100)

def finite(x):
    if isinstance(x, (pd.DataFrame, pd.Series)):
        return x.replace([np.inf, -np.inf], np.nan)
    return np.where(np.isfinite(x), x, np.nan) if np.ndim(x) else x if np.isfinite(x) else np.nan

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
@fixed_factor('annual_ebo_valuation_deviation_1y', {})
class Factor_annual_ebo_valuation_deviation_1y(BaseFactor):
    name = 'annual_ebo_valuation_deviation_1y'
    description = '以当时已公布的年度账面权益和净利润解释市值，残差越大表示相对基本面回归估值更贵，研究市场价格偏离财务价值的程度。 原文：[一个比PE和PB更好的指标——估值偏离度](https://zhuanlan.zhihu.com/p/35103319)。'
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
