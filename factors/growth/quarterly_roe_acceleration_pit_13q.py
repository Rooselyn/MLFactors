"""quarterly_roe_acceleration_pit_13q。

N_q=Q(financial_income.n_income_attr_p); B_q=PITQ(financial_balance_sheet.total_hldr_eqy_exc_min_int); A_q=2*N_q/(B_q+B_(q-1)); Y_q=A_q-A_(q-4); S_q=Mean(A_q,A_(q-4),A_(q-8),A_(q-12))/Std(A_q,A_(q-4),A_(q-8),A_(q-12),ddof=1); P_q=Mean(A_q..A_(q-11)); G_q=A_q-2*A_(q-4)+A_(q-8); F=N_cs(G_q)
在同一行业与规模背景下研究盈利同比改善速度是否进一步增加；类别按经营质量或盈利成长的实际运算选择。 原文：[【研报复现】盈利因子ROE的改进](https://zhuanlan.zhihu.com/p/595717883)。
各季度按利润表YTD差分得到独立单季利润，归母净利润配不含少数股东权益，净资产分母为同季首末均值而非期末值；两期权益都正。每一条历史记录按实际f_ann_date优先、否则ann_date的下一交易日可用，end_date只是报告期，不提前用季末数据。按最新共同已知报告期q及连续历史季度取值，禁止缺季度按行号跳过；四年同季度稳定性需要q到q−12的真实匹配，分母SD正。来源未明确利润少数股东口径和去极值参数，本地明确上述归母口径及截面N(x)：先median±3×1.4826MAD缩尾（MAD=0则不缩尾），再按样本SD标准化，最后对1+ln(10000*circ_mv)+industry_sw_1哑变量OLS取残差；至少100只、行业至少5只，去一列哑变量保满秩，未知不填0。下式N_cs不是样本数。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_income__n_income_attr_p': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'n_income_attr_p', date_column='ann_date', expression='n_income_attr_p', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__ann_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'ann_date', date_column='ann_date', expression='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__f_ann_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'f_ann_date', date_column='ann_date', expression='f_ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__end_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'end_date', date_column='ann_date', expression='end_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__total_hldr_eqy_exc_min_int': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_hldr_eqy_exc_min_int', date_column='ann_date', expression='total_hldr_eqy_exc_min_int', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__ann_date': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'ann_date', date_column='ann_date', expression='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__f_ann_date': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'f_ann_date', date_column='ann_date', expression='f_ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__end_date': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'end_date', date_column='ann_date', expression='end_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'circ_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'circ_mv'), 'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1')}
FORMULA = 'N_q=Q(financial_income.n_income_attr_p); B_q=PITQ(financial_balance_sheet.total_hldr_eqy_exc_min_int); A_q=2*N_q/(B_q+B_(q-1)); Y_q=A_q-A_(q-4); S_q=Mean(A_q,A_(q-4),A_(q-8),A_(q-12))/Std(A_q,A_(q-4),A_(q-8),A_(q-12),ddof=1); P_q=Mean(A_q..A_(q-11)); G_q=A_q-2*A_(q-4)+A_(q-8); F=N_cs(G_q)'
RECIPE = {'family': 'quarterly_roe', 'variant': 'acceleration', 'terms': [['n', 'financial_income', 'n_income_attr_p', 'Q', 1], ['b', 'financial_balance_sheet', 'total_hldr_eqy_exc_min_int', 'B', 1]], 'quarters': 14, 'mode': 'Q'}

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

def log(x, base=np.e, offset=0):
    z = x + offset
    if isinstance(z, (pd.DataFrame, pd.Series)):
        z = z.where(z > 0)
    else:
        z = np.where(z > 0, z, np.nan)
    return np.log(z) / np.log(base)

def neutralize_industry(y, xs, industry, eligible):
    out = y * np.nan
    for d in out.index:
        g = industry.loc[d]
        valid = eligible.loc[d] & g.notna()
        valid &= g.map(g[valid].value_counts()).ge(5)
        yy = y.loc[d, valid]
        design = pd.concat([x.loc[d, valid] for x in xs], axis=1)
        design = pd.concat([pd.Series(1.0, index=yy.index, name='intercept'), design, pd.get_dummies(g[valid], drop_first=True, dtype=float)], axis=1)
        ok = np.isfinite(yy) & np.isfinite(design).all(axis=1)
        (a, b) = (design.loc[ok].to_numpy(float), yy.loc[ok].to_numpy(float))
        if len(b) < 100 or np.linalg.matrix_rank(a) < a.shape[1]:
            continue
        out.loc[d, yy.index[ok]] = b - a @ np.linalg.lstsq(a, b, rcond=None)[0]
    return out

def winsor(x, q=0.01, mad=None):
    if mad is None:
        return x.clip(x.quantile(q, axis=1), x.quantile(1 - q, axis=1), axis=0)
    m = x.median(axis=1)
    s = x.sub(m, axis=0).abs().median(axis=1) * mad
    clipped = x.clip(m - s, m + s, axis=0)
    return clipped.where(s.ne(0), x, axis=0)

def zscore(x, ddof=0, eligible=None):
    if eligible is not None:
        x = x.where(eligible)
    return x.sub(x.mean(axis=1), axis=0).div(x.std(axis=1, ddof=ddof).replace(0, np.nan), axis=0)

def neutralize_research(x, values, eligible):
    return neutralize_industry(zscore(winsor(x.where(eligible), mad=3 * 1.4826), 1), [log(values['circ_mv'] * 10000)], values['industry_sw_1'], eligible)

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
    a = [div(2 * get('n', i), positive(get('b', i)) + positive(get('b', i + 1))) for i in range(13)]
    y = a[0] - a[4]
    s = div(mean(a[::4]), sd(a[::4]))
    p = mean(a[:12])
    g = a[0] - 2 * a[4] + a[8]
    n = lambda x: neutralize_research(x, values, eligible)
    return n({'yoy': y, 'stability': s, 'persistence': p, 'acceleration': g}[variant])

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
@fixed_factor('quarterly_roe_acceleration_pit_13q', {})
class Factor_quarterly_roe_acceleration_pit_13q(BaseFactor):
    name = 'quarterly_roe_acceleration_pit_13q'
    description = '在同一行业与规模背景下研究盈利同比改善速度是否进一步增加；类别按经营质量或盈利成长的实际运算选择。 原文：[【研报复现】盈利因子ROE的改进](https://zhuanlan.zhihu.com/p/595717883)。'
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
