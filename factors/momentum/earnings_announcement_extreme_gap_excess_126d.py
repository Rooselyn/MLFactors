"""earnings_announcement_extreme_gap_excess_126d。

Events=UnionAnnouncementDates(financial_income,financial_earnings_express,financial_earnings_forecast); e=FirstTradingDayAfter(announcement_date); rL=low_hfq[e]/L1(close_hfq)[e]-1; rH=high_hfq[e]/L1(close_hfq)[e]-1; mL=zz500_daily_index.low[e]/L1(zz500_daily_index.close)[e]-1; mH=zz500_daily_index.high[e]/L1(zz500_daily_index.close)[e]-1; G=rH-mH if low_hfq[e]>=L1(close_hfq)[e] else rL-mL if high_hfq[e]<=L1(close_hfq)[e] else rH-mH if abs(rH)>=abs(rL) else rL-mL; F=LatestVisibleEventValue(G,last 126 trading days)
在完整向上、向下跳空时保留对应方向极值，否则取绝对跳空更大一侧，描述盈余公告重估的方向和幅度。 原文：[Python与量化多因子——JOR因子浅析](https://zhuanlan.zhihu.com/p/136125128)。
事件日期来自三张现有财报表的公告日并去重，利润表优先实际公告日f_ann_date；字典无秒级披露时刻，统一保守取公告后的首个市场交易日e，日内发布也不提前到当日。e收盘后才可用，股票e停牌或无有效行情则事件缺失，不把停牌价填0或沿用昨收。个股用已有后复权高低收保持跨日价格一致，中证500与来源基准一致；每日更新时仅保留过去126个交易日内最新有效事件值，超期缺失，不取未来事件。按作者文字“比较两种跳空的绝对值”展开，修正原代码混比abs(ret1)与有符号ret2的笔误；不纳入布尔跳空选股条件。 本地将原6自然月有效期统一为每日滚动126交易日，事件仍以真实公告时点为锚。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from dataloader import read_parquet_table
from factors.base import eligibility
INPUTS = {'financial_income__ann_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'ann_date', date_column='ann_date', expression='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__f_ann_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'f_ann_date', date_column='ann_date', expression='f_ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__end_date': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'end_date', date_column='ann_date', expression='end_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_earnings_express__ann_date': ParquetInput('MLFactors/data/zz500/financial_earnings_express/*/*.parquet', 'ann_date', date_column='ann_date', expression='ann_date', announcement_columns=('ann_date',)), 'financial_earnings_express__end_date': ParquetInput('MLFactors/data/zz500/financial_earnings_express/*/*.parquet', 'end_date', date_column='ann_date', expression='end_date', announcement_columns=('ann_date',)), 'financial_earnings_forecast__ann_date': ParquetInput('MLFactors/data/zz500/financial_earnings_forecast/*/*.parquet', 'ann_date', date_column='ann_date', expression='ann_date', announcement_columns=('ann_date',)), 'financial_earnings_forecast__end_date': ParquetInput('MLFactors/data/zz500/financial_earnings_forecast/*/*.parquet', 'end_date', date_column='ann_date', expression='end_date', announcement_columns=('ann_date',)), 'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'), 'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'), 'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'index_low': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'low', symbol_column=None, expression='low', filters=(('ts_code', '000905.SH'),)), 'index_high': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'high', symbol_column=None, expression='high', filters=(('ts_code', '000905.SH'),)), 'index_close': ParquetInput('MLFactors/data/zz500/zz500_daily_index/*/*.parquet', 'close', symbol_column=None, expression='close', filters=(('ts_code', '000905.SH'),)), 'is_suspended': ParquetInput('MLFactors/data/zz500/zz500_daily_trading_status', 'is_suspended')}
FORMULA = 'Events=UnionAnnouncementDates(financial_income,financial_earnings_express,financial_earnings_forecast); e=FirstTradingDayAfter(announcement_date); rL=low_hfq[e]/L1(close_hfq)[e]-1; rH=high_hfq[e]/L1(close_hfq)[e]-1; mL=zz500_daily_index.low[e]/L1(zz500_daily_index.close)[e]-1; mH=zz500_daily_index.high[e]/L1(zz500_daily_index.close)[e]-1; G=rH-mH if low_hfq[e]>=L1(close_hfq)[e] else rL-mL if high_hfq[e]<=L1(close_hfq)[e] else rH-mH if abs(rH)>=abs(rL) else rL-mL; F=LatestVisibleEventValue(G,last 126 trading days)'
RECIPE = {'family': 'announcement', 'variant': 'extreme'}

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
            prevc = v['close_hfq'].at[prev, s]
            previndex = index_close.at[prev, s]
            lo = div(v['low_hfq'].at[d, s], prevc) - 1
            hi = div(v['high_hfq'].at[d, s], prevc) - 1
            ml = div(v['index_low'].at[d, s], previndex) - 1
            mh = div(v['index_high'].at[d, s], previndex) - 1
            if not np.isfinite([lo, hi, ml, mh]).all():
                continue
            value = lo - ml
            value = hi - mh if lo >= 0 else lo - ml if hi <= 0 else hi - mh if abs(hi) >= abs(lo) else lo - ml
            events.append((d, value, ann))
        for d in dates:
            window = dates[max(0, dates.get_loc(d) - 125)]
            past = [a for a in events if window <= a[0] <= d]
            if past:
                (_, out.at[d, s], available.at[d, s]) = past[-1]
    return (out, available)

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
@fixed_factor('earnings_announcement_extreme_gap_excess_126d', {})
class Factor_earnings_announcement_extreme_gap_excess_126d(BaseFactor):
    name = 'earnings_announcement_extreme_gap_excess_126d'
    description = '在完整向上、向下跳空时保留对应方向极值，否则取绝对跳空更大一侧，描述盈余公告重估的方向和幅度。 原文：[Python与量化多因子——JOR因子浅析](https://zhuanlan.zhihu.com/p/136125128)。'
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
