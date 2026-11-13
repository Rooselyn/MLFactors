"""eps_growth_jump_pit_5q。

E_q=PITQ(financial_indicator.q_eps); g_q=(E_q-E_(q-4))/abs(E_(q-4)); b=(4*g_(q-1)+3*g_(q-2)+2*g_(q-3)+g_(q-4))/30; e_j=g_(q-j)-(5-j)*b,j=1..4; F=(g_q-5*b)/Std(e_1,...,e_4,ddof=0)
对前四个季度的EPS同比增速拟合无截距时间趋势，用最新增速相对外推值的偏离除以拟合误差，衡量盈利成长的突然加速；区别于已有EPS同比变化的历史标准化惊喜。 原文：[EPS增速跳跃因子，大A的基本面因子也不是一无是处！](https://zhuanlan.zhihu.com/p/2068806477872206707)。
沿用原代码时间序号1..4外推至5，无截距；使用字典明确的单季q_eps，避免累计基本EPS的股本分母变化造成差分失真，属于字段口径补全。需连续9个已公告季度、所有同比基期非0、残差总体标准差正；不用交易日移位代替季度移位。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'financial_indicator__q_eps': ParquetInput('MLFactors/data/zz500/financial_indicator/*/*.parquet', 'q_eps', date_column='ann_date', expression='q_eps', announcement_columns=('ann_date',))}
FORMULA = 'E_q=PITQ(financial_indicator.q_eps); g_q=(E_q-E_(q-4))/abs(E_(q-4)); b=(4*g_(q-1)+3*g_(q-2)+2*g_(q-3)+g_(q-4))/30; e_j=g_(q-j)-(5-j)*b,j=1..4; F=(g_q-5*b)/Std(e_1,...,e_4,ddof=0)'
RECIPE = {'family': 'eps_jump', 'terms': [['x', 'financial_indicator', 'q_eps', 'B', 1]], 'quarters': 9, 'mode': 'Q'}

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
    g = [div(get('x', i) - get('x', i + 4), abs(get('x', i + 4))) for i in range(5)]
    b = sum(((4 - i) * g[i + 1] for i in range(4))) / 30
    e = [g[i] - (5 - i) * b for i in range(1, 5)]
    return div(g[0] - 5 * b, sd(e, 0))

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
@fixed_factor('eps_growth_jump_pit_5q', {})
class Factor_eps_growth_jump_pit_5q(BaseFactor):
    name = 'eps_growth_jump_pit_5q'
    description = '对前四个季度的EPS同比增速拟合无截距时间趋势，用最新增速相对外推值的偏离除以拟合误差，衡量盈利成长的突然加速；区别于已有EPS同比变化的历史标准化惊喜。 原文：[EPS增速跳跃因子，大A的基本面因子也不是一无是处！](https://zhuanlan.zhihu.com/p/2068806477872206707)。'
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
