"""five_year_rd_expenditure_to_market_pit_5y。

R_k=AnnualPIT(financial_income.rd_exp)_(y-k),k=0..4; K={k:R_k known}; F=5*Mean(R_k,k in K)/(10000*total_mv), Count(K)>=3 and R_0 known
将五年研发费用累积相对当前市值衡量，研究账面费用化研发可能被市场低估的价值；与单年研发/市值、折旧后研发资本/总资产的分子和估值基准不同。 原文：[经典股市交易思维系列：28、R&D Expenditures Factor（研发支出因子）](https://zhuanlan.zhihu.com/p/592155650)。
本地覆盖修订：五年观测窗至少3个已披露年度、最新年度有效，以有效年度平均研发费用乘5估算五年投入；不再要求五年全部齐全，不以0替代缺失。金额元，total_mv万元，严格按公告后的交易日可用。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_income__rd_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'rd_exp', date_column='ann_date', expression='rd_exp', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv')}
FORMULA = 'R_k=AnnualPIT(financial_income.rd_exp)_(y-k),k=0..4; K={k:R_k known}; F=5*Mean(R_k,k in K)/(10000*total_mv), Count(K)>=3 and R_0 known'
RECIPE = {'family': 'financial_history', 'variant': 'sum_market', 'terms': [['x', 'financial_income', 'rd_exp', 'Y', 4]], 'quarters': 5}

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
    x = [get('x', i) for i in range(recipe['quarters'])]
    arrays = np.stack([a.to_numpy(float) for a in x])
    valid = np.isfinite(arrays)
    count = valid.sum(axis=0)
    average = div(np.nansum(arrays, axis=0), count)
    allowed = (count >= 3) & valid[0]
    wrap = lambda a: pd.DataFrame(a, index=x[0].index, columns=x[0].columns).where(allowed)
    return div(wrap(len(x) * average), 10000 * values['total_mv'].where(values['total_mv'] > 0))

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
@fixed_factor('five_year_rd_expenditure_to_market_pit_5y', {})
class Factor_five_year_rd_expenditure_to_market_pit_5y(BaseFactor):
    name = 'five_year_rd_expenditure_to_market_pit_5y'
    description = '将五年研发费用累积相对当前市值衡量，研究账面费用化研发可能被市场低估的价值；与单年研发/市值、折旧后研发资本/总资产的分子和估值基准不同。 原文：[经典股市交易思维系列：28、R&D Expenditures Factor（研发支出因子）](https://zhuanlan.zhihu.com/p/592155650)。'
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
