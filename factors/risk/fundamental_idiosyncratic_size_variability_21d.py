"""fundamental_idiosyncratic_size_variability_21d。

A=PITQ(financial_balance_sheet.total_assets); B=A-PITQ(financial_balance_sheet.total_liab); L=PITQ(financial_balance_sheet.total_liab)/A; N=LagQ(Q(financial_income.n_income),1); lp=ln(N) if N>0 else 0; lm=ln(-N) if N<0 else 0; D=CS_OLSResidual(ln(stock_day.total_mv)~1+IndustryDummies(stock_day.industry_sw_1)+ln(B)+L+lp+lm); F=SD21(D)
以股票截面基本面解释对数市值，研究基本面解释后市值偏离的近期不稳定性；水平值高对应相对模型内生价值的高估，不因名称含“市值”直接归入规模。 原文：[特异市值，加上“特异”两个字之后，居然变成了一个宝藏因子？](https://zhuanlan.zhihu.com/p/2034792217852766006)。
利润按源码lag=1Q补定为截至信号日最新已公告单季再向前一报告季度，资产余额使用当前已公告可见季度，均受PIT公告时点约束。正负利润分别编码：已知不在该符号区间的列置0，真实缺失利润或资产一律不填0；N=0时两列均0。B、A、市值须正，至少100只完整股票；含截距和去掉一列的行业哑变量，秩不足时以Moore–Penrose最小二乘投影确定唯一拟合与残差。21日水平至少17点，波动须21点、ddof=1。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1'), 'financial_balance_sheet__total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column='ann_date', expression='total_assets', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__total_liab': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_liab', date_column='ann_date', expression='total_liab', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__f_ann_date': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'f_ann_date', date_column='ann_date', expression='f_ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__ann_date': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'ann_date', date_column='ann_date', expression='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__end_date': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'end_date', date_column='ann_date', expression='end_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__n_income': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'n_income', date_column='ann_date', expression='n_income', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__f_ann_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'f_ann_date', date_column='ann_date', expression='f_ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__ann_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'ann_date', date_column='ann_date', expression='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__end_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'end_date', date_column='ann_date', expression='end_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),))}
FORMULA = 'A=PITQ(financial_balance_sheet.total_assets); B=A-PITQ(financial_balance_sheet.total_liab); L=PITQ(financial_balance_sheet.total_liab)/A; N=LagQ(Q(financial_income.n_income),1); lp=ln(N) if N>0 else 0; lm=ln(-N) if N<0 else 0; D=CS_OLSResidual(ln(stock_day.total_mv)~1+IndustryDummies(stock_day.industry_sw_1)+ln(B)+L+lp+lm); F=SD21(D)'
RECIPE = {'family': 'fundamental_size', 'variant': 'variability', 'terms': [['a', 'financial_balance_sheet', 'total_assets', 'B', 1], ['liab', 'financial_balance_sheet', 'total_liab', 'B', 1], ['n', 'financial_income', 'n_income', 'Q', 1]], 'quarters': 2, 'mode': 'Q'}

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

def rolling(x, n, method='mean', ddof=0):
    n = int(n)
    if n < 1:
        raise ValueError('滚动窗口必须为正整数')
    roll = x.rolling(n, min_periods=n)
    if method in ('std', 'var'):
        return getattr(roll, method)(ddof=ddof)
    return getattr(roll, method)()

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
    a = get('a')
    liab = get('liab')
    n = get('n', 1)
    b = a - liab
    lp = log(n.where(n > 0)).where(n > 0, 0).where(n.notna())
    lm = log((-n).where(n < 0)).where(n < 0, 0).where(n.notna())
    x = neutralize_industry(log(values['total_mv']), [log(b), div(liab, a), lp, lm], values['industry_sw_1'], eligible)
    return rolling(x, 21, 'std')

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
@fixed_factor('fundamental_idiosyncratic_size_variability_21d', {})
class Factor_fundamental_idiosyncratic_size_variability_21d(BaseFactor):
    name = 'fundamental_idiosyncratic_size_variability_21d'
    description = '以股票截面基本面解释对数市值，研究基本面解释后市值偏离的近期不稳定性；水平值高对应相对模型内生价值的高估，不因名称含“市值”直接归入规模。 原文：[特异市值，加上“特异”两个字之后，居然变成了一个宝藏因子？](https://zhuanlan.zhihu.com/p/2034792217852766006)。'
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
