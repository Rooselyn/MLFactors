"""three_minute_elasticity_expectation_gap_variability_21d。

aggregate 1m to80 daily3m bars: H_k=Max(stock_minute.high), L_k=Min(stock_minute.low), V_k=Sum(stock_minute.vol); B={k=1..79:L_k=min(L_j,j=max(0,k-13)..min(79,k+13))}; T={k not in B:H_k=max(H_j,same window)}; for b in B: e_b=first T strictly after b; R=Prod(H_(e_b)/L_b over matched b)-1; V=Sum(Sum(V_k,k=b..e_b-1),over matched b); q=M21(R/V); X=R-q*V; F=SD21(CSZ(X)); R=V=0 and R/V:=0 on a complete observed day with no matched rebound; both21day windows remain complete
以局部价格趋势段的单位成交量推动系数估算收益，再研究实际与模型预期差异的跨日不稳定性。 原文：[整一个用3分钟K线计算的因子，顺便和大家聊聊过拟合！](https://zhuanlan.zhihu.com/p/2046401168209974354)。
每半日按3根1分钟分桶，共80根，量股、价元；先判低点、再判高点，等值低点优先，保留来源代码重复极点与相邻配对规则，不另造去重波段算法。每个低点匹配其后第一个高点，无后继不计，允许多个起点配同终点且量重复计入，明确这不是互斥持仓回测。局部前后13根均在当天，盘后已知。R采用源码终高/始低累乘，量区间含起不含终；无配对或V=0缺失，M21(R/V)须21个完整日。原文收益预期差文字与代码反号，此处取代码R−预期，最终标准差对整体反号不变；每日CSZ至少100股，最后SD须21日。
2026-11-06修订：完整有效分钟内没有匹配反弹事件时，R=V=0，日弹性R/V定义为0；未知分钟保持缺失。21日弹性均值和随后21日截面标准化残差波动仍要求完整窗口，不把未发生事件误判为数据未知。"""
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
MINUTE_INPUTS = {'high': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'high', date_column='trade_time'), 'low': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'low', date_column='trade_time'), 'vol': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'vol', date_column='trade_time')}
FORMULA = 'aggregate 1m to80 daily3m bars: H_k=Max(stock_minute.high), L_k=Min(stock_minute.low), V_k=Sum(stock_minute.vol); B={k=1..79:L_k=min(L_j,j=max(0,k-13)..min(79,k+13))}; T={k not in B:H_k=max(H_j,same window)}; for b in B: e_b=first T strictly after b; R=Prod(H_(e_b)/L_b over matched b)-1; V=Sum(Sum(V_k,k=b..e_b-1),over matched b); q=M21(R/V); X=R-q*V; F=SD21(CSZ(X)); R=V=0 and R/V:=0 on a complete observed day with no matched rebound; both21day windows remain complete'
RECIPE = {'family': 'three_minute_elasticity', 'window': 21, 'min_days': 21}

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

def advanced_features(recipe, ctx, k, p, sameclock):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = p.get('close')
    o = p.get('open')
    h = p.get('high')
    l = p.get('low')
    v = p.get('vol')
    a = p.get('amount')
    symbols = ctx.symbols
    nan = pd.Series(np.nan, index=symbols)
    r = div(c, c.shift(1)) - 1 if c is not None else None
    high = h.to_numpy().reshape(80, 3, len(symbols)).max(axis=1)
    low = l.to_numpy().reshape(80, 3, len(symbols)).min(axis=1)
    volume = v.to_numpy().reshape(80, 3, len(symbols)).sum(axis=1)
    ret = nan.copy()
    vol = nan.copy()
    for (j, s) in enumerate(symbols):
        (hh, ll, vv) = (high[:, j], low[:, j], volume[:, j])
        if not (np.isfinite(hh).all() and np.isfinite(ll).all() and np.isfinite(vv).all()):
            continue
        bottom = [i for i in range(1, 80) if ll[i] == ll[max(0, i - 13):min(80, i + 14)].min()]
        top = [i for i in range(1, 80) if i not in bottom and hh[i] == hh[max(0, i - 13):min(80, i + 14)].max()]
        pairs = []
        for b in bottom:
            following = [i for i in top if i > b]
            if following:
                pairs.append((b, following[0]))
        if not pairs:
            # A complete observed day with no rebound has zero event return and volume.
            ret[s] = 0.0
            vol[s] = 0.0
            continue
        ret[s] = np.prod([hh[t] / ll[b] for (b, t) in pairs]) - 1
        vol[s] = sum((vv[b:t].sum() for (b, t) in pairs))
    return {'r': ret, 'v': vol}

def other_features(recipe, ctx, k, p, sameclock):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = p.get('close')
    o = p.get('open')
    h = p.get('high')
    l = p.get('low')
    v = p.get('vol')
    a = p.get('amount')
    symbols = ctx.symbols
    r = div(c, c.shift(1)) - 1 if c is not None else None
    ro = div(c, o) - 1 if o is not None and c is not None else r
    nan = pd.Series(np.nan, index=symbols)
    time = pd.Series(np.arange(1, 241), index=next(iter(p.values())).index)

    def complete(x, n=200):
        valid = np.logical_and.reduce([np.isfinite(x.to_numpy()) for x in p.values()])
        return x.where(valid.sum(axis=0) >= n)
    return advanced_features(recipe, ctx, k, p, sameclock)

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
    return other_features(recipe, ctx, k, p, sameclock)

def rolling(x, n, method='mean', ddof=0):
    n = int(n)
    if n < 1:
        raise ValueError('滚动窗口必须为正整数')
    roll = x.rolling(n, min_periods=n)
    if method in ('std', 'var'):
        return getattr(roll, method)(ddof=ddof)
    return getattr(roll, method)()

def zscore(x, ddof=0, eligible=None):
    if eligible is not None:
        x = x.where(eligible)
    return x.sub(x.mean(axis=1), axis=0).div(x.std(axis=1, ddof=ddof).replace(0, np.nan), axis=0)

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
    elasticity = div(panels['r'], panels['v']).mask(panels['r'].eq(0) & panels['v'].eq(0), 0.0)
    q = rolling(elasticity, 21)
    x = panels['r'] - q * panels['v']
    return rolling(zscore(x, 0, ctx.e.reindex(ctx.days)).where(ctx.e.reindex(ctx.days).sum(axis=1).ge(100), axis=0), 21, 'std')

@register_factor
@fixed_factor('three_minute_elasticity_expectation_gap_variability_21d', {})
class Factor_three_minute_elasticity_expectation_gap_variability_21d(MinuteFactor):
    name = 'three_minute_elasticity_expectation_gap_variability_21d'
    description = '以局部价格趋势段的单位成交量推动系数估算收益，再研究实际与模型预期差异的跨日不稳定性。 原文：[整一个用3分钟K线计算的因子，顺便和大家聊聊过拟合！](https://zhuanlan.zhihu.com/p/2046401168209974354)。 本地修订（2026-11-06）：完整有效分钟内没有匹配反弹事件时，R=V=0，日弹性R/V定义为0；未知分钟保持缺失。21日弹性均值和随后21日截面标准化残差波动仍要求完整窗口，不把未发生事件误判为数据未知。'
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
