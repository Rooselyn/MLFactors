"""unexpected_operating_receipts_working_capital_regression_pit_10q。

B_q=PITQ(financial_balance_sheet.accounts_receiv+financial_balance_sheet.notes_receiv+financial_balance_sheet.prepayment+financial_balance_sheet.inventories); X_q=B_q-LagQ(B_q,1); Y_q=Q(financial_cash_flow.c_fr_sale_sg); b=OLS(Y_s~1+Y_(s-1)+X_s,s=q-8..q-1); e_s=Y_s-Predict(b,s); F=(Y_q-Predict(b,Y_(q-1),X_q))/Std(e_s,ddof=0)
用前期经营结果和应收、票据、预付款、存货的变动估计常态，再以历史预测误差统一当前新息的尺度，衡量销售商品及提供劳务收到现金的意外强弱。 原文：[预期外经营现金流入，这是我见过的分层回测最炸裂的基本面因子！](https://zhuanlan.zhihu.com/p/2072430088902161081)。
回归只训练此前8个财报季度，含截距；当前结果及X也必须已经公告，不能拿未披露财季回填。Q按累计报表拆单季，资产项取各对应季末存量并一阶差分，需要同口径连续10季输入、设计矩阵满秩，训练残差总体标准差正。现金流入明确使用c_fr_sale_sg，不改成n_cashflow_act；净利润版仅依最新文章明确把相同框架的被解释变量替换为净利润，其他解释变量不变。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_cash_flow__c_fr_sale_sg': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'c_fr_sale_sg', date_column='ann_date', expression='c_fr_sale_sg', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__accounts_receiv': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'accounts_receiv', date_column='ann_date', expression='accounts_receiv', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__notes_receiv': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'notes_receiv', date_column='ann_date', expression='notes_receiv', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__prepayment': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'prepayment', date_column='ann_date', expression='prepayment', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_balance_sheet__inventories': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'inventories', date_column='ann_date', expression='inventories', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),))}
FORMULA = 'B_q=PITQ(financial_balance_sheet.accounts_receiv+financial_balance_sheet.notes_receiv+financial_balance_sheet.prepayment+financial_balance_sheet.inventories); X_q=B_q-LagQ(B_q,1); Y_q=Q(financial_cash_flow.c_fr_sale_sg); b=OLS(Y_s~1+Y_(s-1)+X_s,s=q-8..q-1); e_s=Y_s-Predict(b,s); F=(Y_q-Predict(b,Y_(q-1),X_q))/Std(e_s,ddof=0)'
RECIPE = {'family': 'unexpected_quarter', 'terms': [['y', 'financial_cash_flow', 'c_fr_sale_sg', 'Q', 1], ['b1', 'financial_balance_sheet', 'accounts_receiv', 'B', 1], ['b2', 'financial_balance_sheet', 'notes_receiv', 'B', 1], ['b3', 'financial_balance_sheet', 'prepayment', 'B', 1], ['b4', 'financial_balance_sheet', 'inventories', 'B', 1]], 'quarters': 10, 'mode': 'Q'}

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
    out = get('y') * np.nan
    for d in out.index:
        for s in out.columns:
            yy = np.array([get('y', i).at[d, s] for i in range(1, 9)])
            lag = np.array([get('y', i + 1).at[d, s] for i in range(1, 9)])
            change = np.array([sum((get(k, i).at[d, s] - get(k, i + 1).at[d, s] for k in ('b1', 'b2', 'b3', 'b4'))) for i in range(9)])
            a = np.column_stack([np.ones(8), lag, change[1:]])
            cur = np.array([1, get('y', 1).at[d, s], change[0]])
            if not (np.isfinite(a).all() and np.isfinite(yy).all() and np.isfinite(cur).all()) or np.linalg.matrix_rank(a) < 3:
                continue
            b = np.linalg.lstsq(a, yy, rcond=None)[0]
            sigma = (yy - a @ b).std(ddof=0)
            out.at[d, s] = div(get('y').at[d, s] - cur @ b, sigma)
    return out

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
@fixed_factor('unexpected_operating_receipts_working_capital_regression_pit_10q', {})
class Factor_unexpected_operating_receipts_working_capital_regression_pit_10q(BaseFactor):
    name = 'unexpected_operating_receipts_working_capital_regression_pit_10q'
    description = '用前期经营结果和应收、票据、预付款、存货的变动估计常态，再以历史预测误差统一当前新息的尺度，衡量销售商品及提供劳务收到现金的意外强弱。 原文：[预期外经营现金流入，这是我见过的分层回测最炸裂的基本面因子！](https://zhuanlan.zhihu.com/p/2072430088902161081)。'
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
