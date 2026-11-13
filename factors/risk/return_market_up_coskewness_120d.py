"""return_market_up_coskewness_120d。

X=close_hfq/L1(close_hfq)-1; Y=zz500_daily_index.close/L1(zz500_daily_index.close)-1; x=X-Mean120(X); y=Y-Mean120(Y); J={s:y_s>0}; C=Mean(x*y^2 in J)/sqrt(Mean(x^2 in J)*Mean(y^2 in J)); F=C
在市场高于窗口均值时单独考察收益非对称共同暴露，区分上涨环境与下跌环境下的风险偏好。 原文：[协偏度因子选股因子(干货)](https://zhuanlan.zhihu.com/p/686505179)。
已直接查看上下行公式图片：条件样本内分母为sqrt(E[x²∣J]*E[y²∣J])，与全样本σx*σy²不同，不擅自统一。x、y先按全120日窗口均值中心化，再选J；两条件各至少20日。使用已有中证500为明示的本地基准；同一窗口不再扩为240日另计。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'index_close': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'close', symbol_column=None, expression='close', filters=(('ts_code', '000905.SH'),))}
FORMULA = 'X=close_hfq/L1(close_hfq)-1; Y=zz500_daily_index.close/L1(zz500_daily_index.close)-1; x=X-Mean120(X); y=Y-Mean120(Y); J={s:y_s>0}; C=Mean(x*y^2 in J)/sqrt(Mean(x^2 in J)*Mean(y^2 in J)); F=C'
RECIPE = {'family': 'coskew', 'variant': 'up'}

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

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    mr = div(v['index_close'], v['index_close'].shift(1)) - 1
    out = c * np.nan
    for j in range(c.shape[1]):
        (a, b) = (r.iloc[:, j].to_numpy(float), mr.iloc[:, j].to_numpy(float))
        for i in range(119, len(c)):
            (x, y) = (a[i - 119:i + 1], b[i - 119:i + 1])
            good = np.isfinite(x) & np.isfinite(y)
            if good.sum() < 100:
                continue
            (x, y) = (x[good], y[good])
            if min(np.std(x), np.std(y)) <= 0:
                continue
            x = x - x.mean()
            y = y - y.mean()
            m = y > 0
            (x, y) = (x[m], y[m])
            if len(x) < 20:
                continue
            den = np.sqrt(np.mean(x * x) * np.mean(y * y))
            out.iat[i, j] = div(np.mean(x * y * y), den) * 1
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
@fixed_factor('return_market_up_coskewness_120d', {})
class Factor_return_market_up_coskewness_120d(BaseFactor):
    name = 'return_market_up_coskewness_120d'
    description = '在市场高于窗口均值时单独考察收益非对称共同暴露，区分上涨环境与下跌环境下的风险偏好。 原文：[协偏度因子选股因子(干货)](https://zhuanlan.zhihu.com/p/686505179)。'
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
            value = compute_daily(recipe, v, e)
        return finite(value).astype(float).where(e).rename_axis(index='date', columns='symbol')
