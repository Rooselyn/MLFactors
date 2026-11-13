"""earnings_announcement_cumulative_excess_return_4d。

r=close_hfq/L1(close_hfq)-1; m=zz500_daily_index.close/L1(zz500_daily_index.close)-1; e=FirstTradingDayAfter(ActualAnnualOrQuarterAnnouncement); CAR_e=Sum(r_s-m_s,s=e-2..e+1); F=LatestVisible(CAR_e,last 180 calendar days)
以财报披露前后四个交易日超额收益衡量盈利新息的价格反应，研究有限注意力造成的公告后漂移；输出每股公告反应而非所有股票相同的PEAD组合收益。 原文：[一个加入行为因子的复合模型](https://zhuanlan.zhihu.com/p/57314781)。
使用最新已披露实际合并季度或年报；财报仅有日级日期，事件零点补为公告之后首个市场交易日e；直到e+1日收盘才算得完整CAR，下一交易日可用。市场基准明确采用字典中证500，不引入不存在的市场指数；窗口任一天无有效股价/指数则该事件缺失，保留最新有效事件最多180自然日。本文仅取研究中的股票特征CAR，不把共享市场组合收益计作截面因子。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from dataloader import read_parquet_table
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'index_close': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'close', symbol_column=None, expression='close', filters=(('ts_code', '000905.SH'),)), 'financial_income__ann_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'ann_date', date_column='ann_date', expression='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__f_ann_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'f_ann_date', date_column='ann_date', expression='f_ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__end_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'end_date', date_column='ann_date', expression='end_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),))}
FORMULA = 'r=close_hfq/L1(close_hfq)-1; m=zz500_daily_index.close/L1(zz500_daily_index.close)-1; e=FirstTradingDayAfter(ActualAnnualOrQuarterAnnouncement); CAR_e=Sum(r_s-m_s,s=e-2..e+1); F=LatestVisible(CAR_e,last 180 calendar days)'
RECIPE = {'family': 'announcement', 'variant': 'car'}

def read_announcements(inputs, end, symbols):
    sources = {s.path: s for s in inputs.values() if s.announcement_columns and 'financial_' in s.path}
    result = {}
    for (path, s) in sources.items():
        columns = list(dict.fromkeys(['ts_code', 'end_date', *s.announcement_columns, *[k for (k, _) in s.filters]]))
        table = read_parquet_table(path, columns, date_column='end_date', symbol_column='ts_code', end=end, symbols=symbols)
        for (k, v) in s.filters:
            table = table.loc[table[k].astype('string').str.replace('\\.0$', '', regex=True).eq(v)]
        available = pd.to_datetime(table[s.announcement_columns[0]], errors='coerce')
        for k in s.announcement_columns[1:]:
            available = available.fillna(pd.to_datetime(table[k], errors='coerce'))
        result[path.split('/')[-3]] = table.assign(_available=available, end_date=pd.to_datetime(table.end_date, errors='coerce')).dropna(subset=['_available', 'end_date', 'ts_code'])
    return result

def compute_events(recipe, inputs, v, e, dates, symbols):
    out = pd.DataFrame(np.nan, index=dates, columns=symbols)
    available = pd.DataFrame(pd.NaT, index=dates, columns=symbols)
    records = read_announcements(inputs, dates.max(), list(symbols))
    index_close = v['index_close']
    for s in symbols:
        seen = []
        for table in records.values():
            seen.extend(table.loc[table.ts_code.eq(s), '_available'].tolist())
        events = []
        for ann in sorted(set(seen)):
            pos = dates.searchsorted(ann, side='right')
            if pos >= len(dates) or pos < 1:
                continue
            d = dates[pos]
            prev = dates[pos - 1]
            if not e.at[d, s]:
                continue
            if pos < 2 or pos + 1 >= len(dates):
                continue
            rr = v['close_hfq'][s] / v['close_hfq'][s].shift(1) - 1
            mr = index_close[s] / index_close[s].shift(1) - 1
            a = (rr - mr).iloc[pos - 2:pos + 2]
            if a.notna().sum() == 4:
                events.append((dates[pos + 1], a.sum(), ann))
            continue
        for d in dates:
            window = d - pd.Timedelta(days=179)
            past = [a for a in events if window <= a[0] <= d]
            if past:
                (_, out.at[d, s], available.at[d, s]) = past[-1]
    return (out, available)

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
@fixed_factor('earnings_announcement_cumulative_excess_return_4d', {})
class Factor_earnings_announcement_cumulative_excess_return_4d(BaseFactor):
    name = 'earnings_announcement_cumulative_excess_return_4d'
    description = '以财报披露前后四个交易日超额收益衡量盈利新息的价格反应，研究有限注意力造成的公告后漂移；输出每股公告反应而非所有股票相同的PEAD组合收益。 原文：[一个加入行为因子的复合模型](https://zhuanlan.zhihu.com/p/57314781)。'
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
            (value, self.available_ann_dates) = compute_events(recipe, self.INPUTS, v, e, dates, symbols)
        return finite(value).astype(float).where(e).rename_axis(index='date', columns='symbol')
