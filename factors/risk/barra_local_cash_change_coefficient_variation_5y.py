"""barra_local_cash_change_coefficient_variation_5y。

X_k=Y(financial_cash_flow.n_incr_cash_cash_equ)_(y-k),k=0..4; F=-Std(X,ddof=1)/abs(Mean(X)); fit/use only known years in five-year window, minimum 3 and latest year known
现金及等价物净增加额的多年变异系数衡量经营结果相对规模的不稳定性，不对日频前向填充值求标准差。 原文：[知乎BARRA CNE6模型复现引用的公开源码](https://github.com/ShiliangZhang-nku/Barra_CNE6/blob/master/barra_cne6_factor.py)。
本地覆盖修订：五年观测窗至少3个有效年、最新年度有效；斜率按真实年份坐标拟合，缺年不压缩时间；标准差ddof=1，均值取绝对值作分母，均值为0仍缺失。仅用截至当日已公告版本，不插值。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_cash_flow__n_incr_cash_cash_equ': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_incr_cash_cash_equ', date_column='ann_date', expression='n_incr_cash_cash_equ', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),))}
FORMULA = 'X_k=Y(financial_cash_flow.n_incr_cash_cash_equ)_(y-k),k=0..4; F=-Std(X,ddof=1)/abs(Mean(X)); fit/use only known years in five-year window, minimum 3 and latest year known'
RECIPE = {'family': 'financial_history', 'variant': 'cv', 'terms': [['x', 'financial_cash_flow', 'n_incr_cash_cash_equ', 'Y', 4]], 'quarters': 5}

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
    std = np.sqrt(div(np.nansum((arrays - average) ** 2, axis=0), count - 1))
    return wrap(-div(std, abs(average)))

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
@fixed_factor('barra_local_cash_change_coefficient_variation_5y', {})
class Factor_barra_local_cash_change_coefficient_variation_5y(BaseFactor):
    name = 'barra_local_cash_change_coefficient_variation_5y'
    description = '现金及等价物净增加额的多年变异系数衡量经营结果相对规模的不稳定性，不对日频前向填充值求标准差。 原文：[知乎BARRA CNE6模型复现引用的公开源码](https://github.com/ShiliangZhang-nku/Barra_CNE6/blob/master/barra_cne6_factor.py)。'
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
