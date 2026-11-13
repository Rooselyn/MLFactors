"""markov_abnormal_return_following_amount_corr_21d。

r_i,m=stock_minute.close[i,m]/stock_minute.open[i,m]-1; s_i,m=I(r_i,m>0); sM_m=I(CSMean(r_m)>0); pi_a=Mean_day(I(sM=a)); P_ab=Count(sM_m=a and sM_(m+1)=b)/Count(sM_m=a with observed successor); q_i,m=pi_(s_i,m-4)*Prod(P_(s_i,k,s_i,k+1),k=m-4..m-1); qM similarly from sM; J_i,m=I(q_i,m<=Quantile_day(q_i,0.20)),m=5..240; D=Corr(stock_minute.amount[m],stock_minute.amount[m+1],over J_i,m=1 and m=5..239); F=M21(D); abnormal minutes q_i<=own daily Q20(q_i), boundary ties included; corr at least10 valid pairs; M21 min17
识别市场符号转移模型下罕见的个股收益路径，衡量该时刻成交额向下一分钟延续的程度。 原文：[基于马尔科夫链的收益率异常时刻成交额相关性，3年IC绝对值超0.12！](https://zhuanlan.zhihu.com/p/2043084106427266560)。
市场转移概率、五分钟路径概率沿其引用的公开V4代码完整展开，概率统一标在五分钟窗末端，等价消除原代码shift(-4)再shift(1)的起点索引。市场至少100股，两状态各至少5后继，0转移直接得0路径概率；当日异常起点至少10组量额配对且双方方差正，21日至少17日。次分钟仍在信号日盘中，盘后可见，末分钟无后继剔除；不引用信号日后的成交额。
2026-11-06修订：异常路径门槛由市场路径概率5%分位改为每只股票当日自身五步路径概率20%分位，并纳入边界并列值；仍以已知马尔可夫转移估计路径概率，对选中分钟及下一分钟成交额求相关，至少10对，21日均值至少17日。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from collections import OrderedDict
import numpy as np
import pandas as pd
from factors.base import eligibility
from factors.base import MinuteFactor
import warnings
from factors.inputs import read_inputs
INPUTS = {}
MINUTE_INPUTS = {'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time'), 'open': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'open', date_column='trade_time'), 'vol': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'vol', date_column='trade_time'), 'amount': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'amount', date_column='trade_time')}
FORMULA = 'r_i,m=stock_minute.close[i,m]/stock_minute.open[i,m]-1; s_i,m=I(r_i,m>0); sM_m=I(CSMean(r_m)>0); pi_a=Mean_day(I(sM=a)); P_ab=Count(sM_m=a and sM_(m+1)=b)/Count(sM_m=a with observed successor); q_i,m=pi_(s_i,m-4)*Prod(P_(s_i,k,s_i,k+1),k=m-4..m-1); qM similarly from sM; J_i,m=I(q_i,m<=Quantile_day(q_i,0.20)),m=5..240; D=Corr(stock_minute.amount[m],stock_minute.amount[m+1],over J_i,m=1 and m=5..239); F=M21(D); abnormal minutes q_i<=own daily Q20(q_i), boundary ties included; corr at least10 valid pairs; M21 min17'
RECIPE = {'family': 'markov_return', 'variant': 'following', 'window': 21, 'min_days': 17}

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

def grid(day):
    d = pd.Timestamp(day).normalize()
    return pd.date_range(d + pd.Timedelta('9h31min'), d + pd.Timedelta('11h30min'), freq='min').append(pd.date_range(d + pd.Timedelta('13h1min'), d + pd.Timedelta('15h'), freq='min'))

class MinuteContext:

    def __init__(self, daily_data, minute_data, inputs, minute_inputs):
        (self.v, self.dates, self.symbols) = daily_values(daily_data, inputs)
        self.e = eligibility(daily_data, self.dates, self.symbols)
        for f in ('close_hfq', 'total_mv', 'industry_sw_1'):
            if f not in self.v and f in daily_data:
                self.v[f] = daily_data[f].unstack('symbol').reindex(index=self.dates, columns=self.symbols)
        days = pd.DatetimeIndex(minute_data.attrs.get('trade_dates', self.dates)).sort_values()
        self.days = days.intersection(self.dates)
        self.p = {}
        self.cubes = {}
        active = self.e.reindex(index=self.days, columns=self.symbols).fillna(False).any(axis=0)
        self.symbols = self.symbols[active.to_numpy()]
        self.grids = [grid(d) for d in self.days]
        self._day_cache = OrderedDict()
        self._scalar_cache = {}
        self._group_cache = {}
        self.derived = {}
        index = pd.DatetimeIndex(np.concatenate([g.to_numpy() for g in self.grids])) if len(self.days) else pd.DatetimeIndex([])
        wide = None if minute_data.empty else minute_data[list(minute_inputs)].unstack('symbol')
        member = self.e.reindex(index=index.normalize(), columns=self.symbols).fillna(False).to_numpy(bool)
        for f in minute_inputs:
            if minute_data.empty:
                panel = pd.DataFrame(np.nan, index=index, columns=self.symbols)
            else:
                panel = wide[f].reindex(index=index, columns=self.symbols).astype(float)
            panel = panel.where(np.isfinite(panel) & (panel.ge(0) if f in ('vol', 'amount') else panel.gt(0)))
            panel = panel.where(member)
            self.p[f] = panel
        if {'high', 'low'} <= self.p.keys():
            good = self.p['high'] >= self.p['low']
            for f in ('open', 'close'):
                if f in self.p:
                    good &= self.p[f].ge(self.p['low']) & self.p[f].le(self.p['high'])
            for f in self.p:
                self.p[f] = self.p[f].where(good)
        for (f, p) in self.p.items():
            self.cubes[f] = p.to_numpy().reshape(len(self.days), 240, len(self.symbols))

    def day(self, k):
        if k not in self._day_cache:
            self._day_cache[k] = {f: pd.DataFrame(a[k], index=self.grids[k], columns=self.symbols, copy=False) for (f, a) in self.cubes.items()}
        self._day_cache.move_to_end(k)
        while len(self._day_cache) > 22:
            self._day_cache.popitem(last=False)
        return self._day_cache[k]

def div(a, b):
    if isinstance(b, (pd.DataFrame, pd.Series)):
        b = b.where(np.isfinite(b) & b.ne(0))
    elif np.ndim(b):
        b = np.where(np.isfinite(b) & (b != 0), b, np.nan)
    elif not np.isfinite(b) or b == 0:
        b = np.nan
    with np.errstate(all='ignore'):
        return finite(a / b)

def aggregate_features(frame, recipe):
    n = recipe.get('window', 21)
    minimum = recipe.get('min_days', n)
    operation = recipe.get('aggregation', 'mean')
    roll = frame.rolling(n, min_periods=minimum)
    if operation == 'inverse_cv':
        value = div(roll.mean(), roll.std(ddof=recipe.get('ddof', 1)))
    elif operation in ('std', 'var'):
        value = getattr(roll, operation)(ddof=recipe.get('ddof', 0))
    else:
        value = getattr(roll, operation)()
    value.iloc[:n - 1] = np.nan
    return value * recipe.get('sign', 1)

def corr(a, b, minimum=3):
    valid = a.notna() & b.notna()
    (aa, bb) = (a.where(valid), b.where(valid))
    return aa.corrwith(bb).where(valid.sum() >= minimum).where(aa.std() > 0).where(bb.std() > 0)

def markov_path(states, market, minimum=5):
    m = market.to_numpy(float)
    good = np.isfinite(m[:-1]) & np.isfinite(m[1:])
    counts = np.zeros((2, 2))
    for (a, b) in zip(m[:-1][good], m[1:][good]):
        counts[int(a), int(b)] += 1
    if np.any(counts.sum(axis=1) < minimum):
        return (states * np.nan, pd.Series(np.nan, index=states.index))
    prob = counts / counts.sum(axis=1)[:, None]
    pi = np.array([(m == a).sum() / np.isfinite(m).sum() for a in range(2)])

    def calc(s):
        out = np.full(s.shape, np.nan)
        if len(s) < 5:
            return out
        paths = np.lib.stride_tricks.sliding_window_view(s, 5, axis=0)
        valid = np.isfinite(paths).all(axis=-1)
        codes = np.where(np.isfinite(paths), paths, 0).astype(int)
        value = pi[codes[..., 0]] * np.prod(prob[codes[..., :-1], codes[..., 1:]], axis=-1)
        out[4:] = np.where(valid, value, np.nan)
        return out
    return (pd.DataFrame(calc(states.to_numpy()), index=states.index, columns=states.columns), pd.Series(calc(m), index=states.index))

def history_features(recipe, ctx, k, p, sameclock):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = p.get('close')
    o = p.get('open')
    v = p.get('vol')
    a = p.get('amount')
    r = div(c, c.shift(1)) - 1 if c is not None else None
    ro = div(c, o) - 1 if o is not None and c is not None else r
    nan = pd.Series(np.nan, index=ctx.symbols)
    market = ro.mean(axis=1).where(ro.count(axis=1) >= 100)
    states = (ro > 0).astype(float).where(ro.notna())
    ms = (market > 0).astype(float).where(market.notna())
    (q, qm) = markov_path(states, ms)
    # Use each stock's lower fifth of observed path probabilities; include boundary ties.
    threshold = q.quantile(0.2)
    select = q.le(threshold, axis='columns') & q.notna()
    return {'d': corr(a.where(select), a.shift(-1).where(select), 10)}

def day_features(recipe, ctx, k):
    p = ctx.day(k)
    family = recipe['family']
    variant = recipe.get('variant', '')
    symbols = ctx.symbols
    day = ctx.days[k]
    nan = pd.Series(np.nan, index=symbols)
    c = p.get('close')
    o = p.get('open')
    h = p.get('high')
    l = p.get('low')
    v = p.get('vol')
    a = p.get('amount')
    r = div(c, c.shift(1)) - 1 if c is not None else None
    ro = div(c, o) - 1 if c is not None and o is not None else r
    time = pd.Series(np.arange(1, 241, dtype=float), index=next(iter(p.values())).index)

    def complete(x, minimum=200, fields=None):
        valid = pd.DataFrame(True, index=time.index, columns=symbols)
        for f in fields or list(p):
            valid &= p[f].notna()
        return x.where(valid.sum() >= minimum)

    def sameclock(x, n=21, min_days=21, method='z', prior=False):
        arrays = []
        end = k if prior else k + 1
        for i in range(max(0, end - n), end):
            arrays.append(x(ctx.day(i), i).to_numpy())
        if len(arrays) < min_days:
            return pd.DataFrame(np.nan, index=time.index, columns=symbols)
        z = np.stack(arrays)
        count = np.isfinite(z).sum(axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            mu = np.nanmean(z, axis=0)
            sd = np.nanstd(z, axis=0, ddof=1)
        cur = x(p, k).to_numpy()
        result = mu if method == 'mean' else sd if method == 'std' else div(cur - mu, sd)
        return pd.DataFrame(np.where(count >= min_days, result, np.nan), index=time.index, columns=symbols)
    return history_features(recipe, ctx, k, p, sameclock)

def compute_minute(recipe, ctx):
    family = recipe['family']
    variant = recipe.get('variant', '')
    gathered = []
    cache = getattr(ctx, 'feature_cache', {})
    for (k, d) in enumerate(ctx.days):
        if d not in cache:
            cache[d] = day_features(recipe, ctx, k)
        stats_today = cache[d]
        gathered.append(stats_today)
    keys = set().union(*(x.keys() for x in gathered)) if gathered else {'d'}
    panels = {key: pd.DataFrame([x.get(key, pd.Series(np.nan, index=ctx.symbols)) for x in gathered], index=ctx.days, columns=ctx.symbols) for key in keys}
    panel = panels.get('d')
    return aggregate_features(panel, recipe)

@register_factor
@fixed_factor('markov_abnormal_return_following_amount_corr_21d', {})
class Factor_markov_abnormal_return_following_amount_corr_21d(MinuteFactor):
    name = 'markov_abnormal_return_following_amount_corr_21d'
    description = '识别市场符号转移模型下罕见的个股收益路径，衡量该时刻成交额向下一分钟延续的程度。 原文：[基于马尔科夫链的收益率异常时刻成交额相关性，3年IC绝对值超0.12！](https://zhuanlan.zhihu.com/p/2043084106427266560)。 本地修订（2026-11-06）：异常路径门槛由市场路径概率5%分位改为每只股票当日自身五步路径概率20%分位，并纳入边界并列值；仍以已知马尔可夫转移估计路径概率，对选中分钟及下一分钟成交额求相关，至少10对，21日均值至少17日。'
    INPUTS = INPUTS
    FORMULA = FORMULA
    RECIPE = RECIPE
    MINUTE_INPUTS = MINUTE_INPUTS
    PRESERVE_REPORT_HISTORY = True
    warmup_days = 100000

    def __init__(self):
        super().__init__(tuple(self.MINUTE_INPUTS), minute_window_days=100)

    def _compute(self, daily_data, minute_data):
        context = MinuteContext(daily_data, minute_data, self.INPUTS, self.MINUTE_INPUTS)
        with np.errstate(all='ignore'):
            result = compute_minute(self.RECIPE, context)
        return finite(result).astype(float).where(context.e.reindex(result.index)).rename_axis(index='date', columns='symbol')

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        minute_data = minute_data.loc[minute_data.index.get_level_values('trade_time').normalize() <= trade_date].copy()
        daily_data = daily_data.loc[daily_data.index.get_level_values('date') <= trade_date]
        result = self._compute(daily_data, minute_data)
        return result.reindex(index=[trade_date], columns=symbols).iloc[0]

    def generate_minute_signals(self, daily_data, data_loader):
        ff_cache = None
        signal_dates = pd.DatetimeIndex(data_loader.trading_calendar).sort_values()
        history = pd.DatetimeIndex(data_loader.history_calendar).sort_values()
        parts = []
        feature_cache = {}
        minute_buffer = None
        loaded_until = None
        symbols = daily_data.index.get_level_values('symbol').unique().sort_values()
        for month in signal_dates.to_period('M').unique():
            output_dates = signal_dates[signal_dates.to_period('M') == month]
            position = history.searchsorted(output_dates[0])
            start = max(0, position - self.minute_window_days)
            days = history[start:history.searchsorted(output_dates[-1], side='right')]
            read_start = days[0] if loaded_until is None else max(days[0], loaded_until + pd.Timedelta(days=1))
            new_rows = read_inputs(self.MINUTE_INPUTS, start=read_start, end=days[-1], symbols=symbols).rename_axis(index=['trade_time', 'symbol'])
            if minute_buffer is None or minute_buffer.empty:
                minute_buffer = new_rows
            elif not new_rows.empty:
                minute_buffer = pd.concat([minute_buffer, new_rows])
            minute_buffer = minute_buffer.loc[minute_buffer.index.get_level_values('trade_time') >= days[0]]
            minute = minute_buffer
            loaded_until = days[-1]
            if minute.empty:
                parts.append(pd.DataFrame(np.nan, index=output_dates, columns=symbols))
                print(f"MINUTE_PROGRESS factor={self.name} month={month} output_days={signal_dates.searchsorted(output_dates[-1], side='right')}/{len(signal_dates)} empty_input=True", flush=True)
                continue
            minute.attrs['trade_dates'] = tuple(days)
            data = daily_data.loc[daily_data.index.get_level_values('date') <= days[-1]]
            context = MinuteContext(data, minute, self.INPUTS, self.MINUTE_INPUTS)
            if ff_cache is not None:
                context.v['_ff_local'] = ff_cache
            context.feature_cache = feature_cache
            with np.errstate(all='ignore'):
                result = compute_minute(self.RECIPE, context)
            result = finite(result).astype(float).where(context.e.reindex(result.index)).reindex(output_dates)
            feature_cache = {d: value for (d, value) in feature_cache.items() if d >= days[0]}
            parts.append(result)
            print(f"MINUTE_PROGRESS factor={self.name} month={month} output_days={signal_dates.searchsorted(output_dates[-1], side='right')}/{len(signal_dates)}", flush=True)
            del context
        value = pd.concat(parts).reindex(index=signal_dates, columns=symbols) if parts else pd.DataFrame(index=signal_dates, columns=symbols, dtype=float)
        return value.rename_axis(index='date', columns='symbol')
