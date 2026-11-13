"""organization_capital_to_fix_assets_pit_1y。

X_y=AnnualPIT(financial_income.sell_exp+financial_income.admin_exp); OC_y=0.8*OC_(y-1)+0.3*X_y; OC_0=0.3*X_0/(0.10+0.20); F=OC_y/AnnualPIT(financial_balance_sheet.fix_assets); require at least3 consecutive known annual expense reports including latest; nonnegative expenses; financial industries excluded
将销售管理费用中形成可持续组织能力的部分资本化，按永续盘存法积累后相对固定资产衡量组织资本强度；属于长期经营能力代理，不能将所有费用认定为有效资产。 原文：[Stata学习：如何构建企业组织资本变量？](https://zhuanlan.zhihu.com/p/696897677)。
按原文基准θ=0.3、折旧δ=0.2，仅保留一个基准参数版本；原文全样本费用平均增速会引入未来信息，初始化改用固定g=10%并明确为本地补全。要求至少连续3年已公告财务历史，缺年不跳过递推；费用缺失不填0、负费用留缺失，分母须正，金融业缺失。
2026-11-06修订：组织资本保留固定增长10%、费用资本化30%、折旧20%的永续盘存；最低连续已公告年度由5年调整为3年，最新年必须有效，断年不跳过。递推用NumPy数组等价向量化，避免逐日逐股逐年度DataFrame取值；保留金融业剔除和正分母限制。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_income__sell_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'sell_exp', date_column='ann_date', expression='sell_exp', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__admin_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'admin_exp', date_column='ann_date', expression='admin_exp', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__fix_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'fix_assets', date_column='ann_date', expression='fix_assets', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'industry_sw_1': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'industry_sw_1')}
FORMULA = 'X_y=AnnualPIT(financial_income.sell_exp+financial_income.admin_exp); OC_y=0.8*OC_(y-1)+0.3*X_y; OC_0=0.3*X_0/(0.10+0.20); F=OC_y/AnnualPIT(financial_balance_sheet.fix_assets); require at least3 consecutive known annual expense reports including latest; nonnegative expenses; financial industries excluded'
RECIPE = {'family': 'organization_capital', 'terms': [['sell', 'financial_income', 'sell_exp', 'Y', 4], ['admin', 'financial_income', 'admin_exp', 'Y', 4], ['den', 'financial_balance_sheet', 'fix_assets', 'Y', 4]], 'quarters': 40}

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
    x = np.stack([(get('sell', i) + get('admin', i)).to_numpy(float) for i in range(recipe['quarters'])])
    known = np.isfinite(x) & (x >= 0)
    length = np.cumprod(known, axis=0).sum(axis=0)
    capital = np.full(x.shape[1:], np.nan)
    for i in range(len(x) - 1, -1, -1):
        capital = np.where(length == i + 1, x[i], capital)
        capital = np.where(length > i + 1, 0.8 * capital + 0.3 * x[i], capital)
    capital[length < 3] = np.nan
    out = div(pd.DataFrame(capital, index=get('den').index, columns=get('den').columns), positive(get('den')))
    return out.where(~values['industry_sw_1'].astype('string').apply(lambda s: s.str.contains('银行|非银|金融', na=True)))

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
@fixed_factor('organization_capital_to_fix_assets_pit_1y', {})
class Factor_organization_capital_to_fix_assets_pit_1y(BaseFactor):
    name = 'organization_capital_to_fix_assets_pit_1y'
    description = '将销售管理费用中形成可持续组织能力的部分资本化，按永续盘存法积累后相对固定资产衡量组织资本强度；属于长期经营能力代理，不能将所有费用认定为有效资产。 原文：[Stata学习：如何构建企业组织资本变量？](https://zhuanlan.zhihu.com/p/696897677)。 本地修订（2026-11-06）：组织资本保留固定增长10%、费用资本化30%、折旧20%的永续盘存；最低连续已公告年度由5年调整为3年，最新年必须有效，断年不跳过。递推用NumPy数组等价向量化，避免逐日逐股逐年度DataFrame取值；保留金融业剔除和正分母限制。'
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
