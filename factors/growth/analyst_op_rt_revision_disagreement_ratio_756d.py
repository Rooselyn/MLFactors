"""analyst_op_rt_revision_disagreement_ratio_756d。

pairs=last two forecasts per team for FY0+1 within 756 calendar days; d=new-old; F=Mean(d)/sqrt(Mean(d*d)); F=0 iff all known d=0; minimum 1 paired team
用营业收入预测调整的平均幅度除以团队间调整分歧，衡量修正方向的一致程度；保留金额差或每股差，不误写成相对增长率的离散度。 原文：[读研报系列（一）：分析师预期修正](https://zhuanlan.zhihu.com/p/609932725)。
本地覆盖修订：预测记录逐日回看756自然日，只使用发布日不晚于信号日、同一预测财年、每团队最后一次有效记录；至少1团队，EPS分歧至少2团队。财报实际值采用严格公告后可用，不使用未来年度实际值。修正中位数改为有界对称变化，避免基准为0；分歧比改为均值/RMS的方向一致性，已观测修正全为0时取0。配对至少1团队，不制造不存在的配对。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
from factors.base import _formula_calculations
import numpy as np
import re
import pandas as pd
from dataloader import read_parquet_table
from factors.base import eligibility
INPUTS = {'broker_earnings_forecast__op_rt': ParquetInput('MLFactors/data/zz500/broker_earnings_forecast/*/*.parquet', 'op_rt', date_column='report_date', expression='op_rt', announcement_columns=('report_date',), report_period_column='quarter'), 'broker_earnings_forecast__quarter': ParquetInput('MLFactors/data/zz500/broker_earnings_forecast/*/*.parquet', 'quarter', date_column='report_date', expression='quarter', announcement_columns=('report_date',), report_period_column='quarter'), 'broker_earnings_forecast__report_date': ParquetInput('MLFactors/data/zz500/broker_earnings_forecast/*/*.parquet', 'report_date', date_column='report_date', expression='report_date', announcement_columns=('report_date',), report_period_column='quarter'), 'broker_earnings_forecast__org_name': ParquetInput('MLFactors/data/zz500/broker_earnings_forecast/*/*.parquet', 'org_name', date_column='report_date', expression='org_name', announcement_columns=('report_date',), report_period_column='quarter'), 'broker_earnings_forecast__author_name': ParquetInput('MLFactors/data/zz500/broker_earnings_forecast/*/*.parquet', 'author_name', date_column='report_date', expression='author_name', announcement_columns=('report_date',), report_period_column='quarter'), 'financial_income__basic_eps': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'basic_eps', date_column='ann_date', expression='basic_eps', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__n_income': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'n_income', date_column='ann_date', expression='n_income', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column='ann_date', expression='revenue', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),))}
FORMULA = 'pairs=last two forecasts per team for FY0+1 within 756 calendar days; d=new-old; F=Mean(d)/sqrt(Mean(d*d)); F=0 iff all known d=0; minimum 1 paired team'
RECIPE = {'family': 'analyst', 'variant': 'revision_disagreement', 'field': 'op_rt', 'window_days': 756, 'minimum_teams': 1, 'symmetric_revision': True}

def annual_year(label):
    text = str(label).strip().upper()
    m = re.fullmatch('(\\d{4})(?:Q4|年报|年度|年|FY)?', text)
    return int(m.group(1)) if m else np.nan

def clean_team_records(frame, fields):
    frame = frame.copy()
    frame['report_date'] = pd.to_datetime(frame.report_date, errors='coerce')
    for k in ('org_name', 'author_name'):
        frame[k] = frame[k].astype('string').str.strip()
    frame = frame.loc[frame.report_date.notna() & frame.org_name.notna() & frame.author_name.notna() & frame.org_name.ne('') & frame.author_name.ne('')]
    frame['_year'] = frame.quarter.map(annual_year)
    keys = ['ts_code', '_year', 'org_name', 'author_name', 'report_date']
    for f in fields:
        frame[f] = pd.to_numeric(frame[f], errors='coerce').replace([np.inf, -np.inf], np.nan)
        conflict = frame.groupby(keys, dropna=False)[f].transform('nunique', dropna=False).gt(1)
        frame.loc[conflict, f] = np.nan
    return frame[keys + fields].drop_duplicates(keys).sort_values('report_date', kind='stable')

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

def latest_teams(frame, date, year, field, pairs=False, window_days=90):
    left = frame.report_date.searchsorted(date - pd.Timedelta(days=window_days - 1), side='left')
    right = frame.report_date.searchsorted(date, side='right')
    f = frame.iloc[left:right]
    f = f.loc[f._year.eq(year)]
    f = f.loc[f[field].notna()].sort_values('report_date', kind='stable')
    if pairs:
        groups = f.groupby(['org_name', 'author_name'], sort=False)
        values = []
        for (_, g) in groups:
            if len(g) >= 2:
                values.append((g[field].iloc[-2], g[field].iloc[-1]))
        return np.asarray(values, float).reshape(-1, 2)
    return f.drop_duplicates(['org_name', 'author_name'], keep='last')

def compute_events(recipe, inputs, v, e, dates, symbols):
    out = pd.DataFrame(np.nan, index=dates, columns=symbols)
    available = pd.DataFrame(pd.NaT, index=dates, columns=symbols)
    financial_inputs = {k: s for (k, s) in inputs.items() if 'financial_' in s.path}
    which = recipe['variant']
    reports = _formula_calculations.read_reports(financial_inputs, end=dates.max(), symbols=list(symbols)) if financial_inputs else {}
    income = reports.get('financial_income', pd.DataFrame(columns=['_period']))
    annual = income.loc[income._period.mod(4).eq(3)]
    broker_sources = [s for s in inputs.values() if 'broker_earnings_forecast' in s.path]
    fields = sorted({s.field for s in broker_sources} - {'quarter', 'report_date', 'org_name', 'author_name', 'report_title'})
    cols = ['ts_code', 'quarter', 'report_date', 'org_name', 'author_name', *fields]
    raw = read_parquet_table(broker_sources[0].path, cols, date_column='report_date', symbol_column='ts_code', end=dates.max(), symbols=symbols)
    broker = clean_team_records(raw, fields)
    bysym = {s: g for (s, g) in broker.groupby('ts_code', sort=False)}
    actual_by_symbol = {s: g for (s, g) in annual.groupby('ts_code', sort=False)}
    window_days = recipe.get('window_days', 90)
    minimum_teams = recipe.get('minimum_teams', 3)
    forecast_cache = {}
    field = recipe.get('field', 'np')

    def actual(s, date, field=None, first=False):
        a = actual_by_symbol.get(s, annual.iloc[:0])
        a = a.iloc[:a._available.searchsorted(date, side='left')]
        if a.empty:
            return None
        period = a._period.max()
        a = a.loc[a._period.eq(period)].sort_values('_available')
        return a.iloc[0 if first else -1]

    def forecast(s, date, year, col):
        key = (s, date, year, col)
        if key not in forecast_cache:
            f = latest_teams(bysym.get(s, broker.iloc[:0]), date, year, col, window_days=window_days)
            forecast_cache[key] = f[col].mean() if len(f) >= minimum_teams else np.nan
        return forecast_cache[key]
    for s in symbols:
        forecast_cache.clear()
        f = bysym.get(s, broker.iloc[:0])
        for (i, d) in enumerate(dates):
            if not e.at[d, s]:
                continue
            a = actual(s, d)
            if a is None:
                continue
            year = int(a._period // 4)
            available.at[d, s] = a._available
            if which in ('revision_median', 'revision_breadth', 'revision_disagreement'):
                pairs = latest_teams(f, d, year + 1, field, pairs=True, window_days=window_days)
                if len(pairs) < minimum_teams:
                    continue
                (old, new) = pairs.T
                delta = new - old
                if which == 'revision_median':
                    rel = np.divide(delta, abs(old) + abs(new), out=np.zeros_like(delta), where=abs(old) + abs(new) > 0)
                    rel = rel[np.isfinite(rel)]
                    if len(rel) >= minimum_teams:
                        out.at[d, s] = np.median(rel)
                elif which == 'revision_breadth':
                    out.at[d, s] = (1 + np.mean(delta > 0)) / (1 + np.mean(delta < 0))
                else:
                    rms = np.sqrt(np.mean(delta ** 2))
                    out.at[d, s] = delta.mean() / rms if rms > 0 else 0.0
            elif which == 'yield':
                out.at[d, s] = div(forecast(s, d, year + 1, 'np'), v['total_mv'].at[d, s])
            elif which == 'growth':
                out.at[d, s] = div(10000 * forecast(s, d, year + 1, field), a['n_income' if field == 'np' else 'revenue']) - 1
            elif which in ('fy1_revision', 'fy3_revision', 'revision_gap'):

                def change(k, h):
                    if i < h:
                        return np.nan
                    current = forecast(s, d, year + k, field)
                    past = forecast(s, dates[i - h], year + k, field)
                    return div(current, past) - 1
                if which == 'revision_gap':
                    out.at[d, s] = change(3, 63) - change(1, 63)
                else:
                    k = 1 if which == 'fy1_revision' else 3
                    lags = (63, 126) if k == 1 else (21, 63, 126)
                    changes = np.asarray([change(k, h) for h in lags])
                    known = changes[np.isfinite(changes)]
                    if len(known) >= len(lags):
                        out.at[d, s] = known.mean()
            elif which == 'dispersion':
                teams = latest_teams(f, d, year + 1, 'eps', window_days=window_days)
                if len(teams) >= max(2, minimum_teams):
                    out.at[d, s] = -div(teams.eps.std(ddof=0), v['close'].at[d, s])
            elif which.startswith('realized_'):
                first = actual(s, d, first=True)
                yr = int(first._period // 4)
                ann = first._available
                actual_value = first.n_income / 10000
                if not np.isfinite(actual_value):
                    continue
                start = ann - pd.Timedelta(days=window_days - 1)
                forecasts = f.loc[f._year.eq(yr) & f.report_date.ge(start) & f.report_date.lt(ann) & f.np.notna()].drop_duplicates(['org_name', 'author_name'], keep='last')
                if len(forecasts) < minimum_teams:
                    continue
                errors = forecasts.np - actual_value
                value = -abs(errors.mean()) if which == 'realized_consensus' else -abs(errors).mean() if which == 'realized_absolute' else -errors.mean()
                out.at[d, s] = div(value, v['total_mv'].at[d, s])
            else:
                raise ValueError(f'未实现券商预测配方: {which}')
    return (finite(out), available)

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
@fixed_factor('analyst_op_rt_revision_disagreement_ratio_756d', {})
class Factor_analyst_op_rt_revision_disagreement_ratio_756d(BaseFactor):
    name = 'analyst_op_rt_revision_disagreement_ratio_756d'
    description = '用营业收入预测调整的平均幅度除以团队间调整分歧，衡量修正方向的一致程度；保留金额差或每股差，不误写成相对增长率的离散度。 原文：[读研报系列（一）：分析师预期修正](https://zhuanlan.zhihu.com/p/609932725)。'
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
