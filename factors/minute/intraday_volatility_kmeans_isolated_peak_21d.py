"""intraday_volatility_kmeans_isolated_peak_21d。

O=stock_minute.open; C=stock_minute.close; H=stock_minute.high; L=stock_minute.low; r=C/LagMinute(C)-1; v1=Std(all 20 O,H,L,C values in last 5 minutes,ddof=0)/Mean(same 20 values); v2=Std5(r,ddof=1); v3=sqrt(Sum5(ln(H/L)^2)/(20*ln(2))); v4=sqrt(Mean5(0.5*ln(H/L)^2-(2*ln(2)-1)*ln(C/O)^2)); v5=sqrt(Mean5(ln(H/C)*ln(H/O)+ln(L/C)*ln(L/O))); labels=KMeans2([v1..v5] at minutes 6..240); h=cluster whose center is larger on at least 3 of 5 coordinates; E_m=I(label_m=h); Peak_m=E_m*(1-E_(m-1))*(1-E_(m+1)); D=Sum(Peak_m); F=M21(D)
结合五类日内波动估计，以当日无监督聚类识别相对高低波动状态，统计孤立高波动时点的出现频率。聚类标签只作中间选择，最终输出多日数量强度。 原文：[邪修成功！我计算了五种波动率，然后用k-means将其聚类后，得到波谷分钟数因子！](https://zhuanlan.zhihu.com/p/2028233293938607143)。
严格保留来源五维原值，不额外Z化。首个相邻收盘收益在日内计算，m=6后五点窗已完整；完整240分钟形成235个观测，日内sqrt项非负且全有效。KMeans补为欧氏距离、k-means++、n_init=10、random_state=0、max_iter=300、tol=1e-4，选平方误差最小已收敛解；两中心重合时缺失。五维多数比较给出高波标签，首尾邻居补False仅用于孤立点判定，不跨日；21日至少17有效日。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from collections import OrderedDict
import numpy as np
import pandas as pd
from factors.base import eligibility
from factors.base import MinuteFactor
from sklearn.cluster import KMeans
import warnings
from factors.inputs import read_inputs
INPUTS = {}
MINUTE_INPUTS = {'open': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'open', date_column='trade_time'), 'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time'), 'high': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'high', date_column='trade_time'), 'low': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'low', date_column='trade_time')}
FORMULA = 'O=stock_minute.open; C=stock_minute.close; H=stock_minute.high; L=stock_minute.low; r=C/LagMinute(C)-1; v1=Std(all 20 O,H,L,C values in last 5 minutes,ddof=0)/Mean(same 20 values); v2=Std5(r,ddof=1); v3=sqrt(Sum5(ln(H/L)^2)/(20*ln(2))); v4=sqrt(Mean5(0.5*ln(H/L)^2-(2*ln(2)-1)*ln(C/O)^2)); v5=sqrt(Mean5(ln(H/C)*ln(H/O)+ln(L/C)*ln(L/O))); labels=KMeans2([v1..v5] at minutes 6..240); h=cluster whose center is larger on at least 3 of 5 coordinates; E_m=I(label_m=h); Peak_m=E_m*(1-E_(m-1))*(1-E_(m+1)); D=Sum(Peak_m); F=M21(D)'
RECIPE = {'family': 'volatility_kmeans', 'variant': 'peak', 'window': 21, 'min_days': 17}

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

def log(x, base=np.e, offset=0):
    z = x + offset
    if isinstance(z, (pd.DataFrame, pd.Series)):
        z = z.where(z > 0)
    else:
        z = np.where(z > 0, z, np.nan)
    return np.log(z) / np.log(base)

def ohlc_dispersion(p, n):
    arrays = np.stack([p[f].to_numpy() for f in ('open', 'high', 'low', 'close')])
    out = p['close'] * np.nan
    for i in range(n - 1, len(out)):
        a = arrays[:, i - n + 1:i + 1, :].reshape(4 * n, out.shape[1])
        out.iloc[i] = div(a.std(axis=0), a.mean(axis=0))
    return out

def rolling(x, n, method='mean', ddof=0):
    n = int(n)
    if n < 1:
        raise ValueError('滚动窗口必须为正整数')
    roll = x.rolling(n, min_periods=n)
    if method in ('std', 'var'):
        return getattr(roll, method)(ddof=ddof)
    return getattr(roll, method)()

def model_features(recipe, ctx, k, p):
    family = recipe['family']
    variant = recipe['variant']
    c = p['close']
    v = p.get('vol')
    a = p.get('amount')
    r = div(c, c.shift(1)) - 1
    out = pd.Series(np.nan, index=ctx.symbols)
    vwap = out.copy()
    all_vwap = out.copy()
    vol = ohlc_dispersion(p, 5)
    for s in ctx.symbols:
        (o, h, l) = (p['open'][s], p['high'][s], p['low'][s])
        cc = c[s]
        features = pd.concat([vol[s], r[s].rolling(5, min_periods=5).std(ddof=1), np.sqrt(rolling(log(div(h, l)) ** 2, 5, 'sum') / (20 * np.log(2))), np.sqrt(rolling(0.5 * log(div(h, l)) ** 2 - (2 * np.log(2) - 1) * log(div(cc, o)) ** 2, 5)), np.sqrt(rolling(log(div(h, cc)) * log(div(h, o)) + log(div(l, cc)) * log(div(l, o)), 5))], axis=1).iloc[5:]
        good = np.isfinite(features).all(axis=1)
        if good.sum() != 235 or c[s].count() != 240:
            continue
        x = features.loc[good].to_numpy()
        model = KMeans(n_clusters=2, n_init=10, random_state=0, max_iter=300, tol=0.0001).fit(x)
        labels = model.labels_
        centers = model.cluster_centers_
        if model.n_iter_ >= 300 or np.max(abs(centers[0] - centers[1])) <= 1e-12:
            continue
        larger = (centers[0] > centers[1]).sum()
        high = 0 if larger >= 3 else 1 if (centers[1] > centers[0]).sum() >= 3 else None
        if high is None:
            continue
        states = pd.Series(np.nan, index=c.index)
        states.loc[features.index[good]] = (labels == high).astype(float)
        out[s] = (states.eq(1) & states.shift(1).fillna(0).eq(0) & states.shift(-1).fillna(0).eq(0)).sum()
        continue
    return {'d': out, 'vwap': vwap, 'all_vwap': all_vwap}

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
    return model_features(recipe, ctx, k, p)

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
@fixed_factor('intraday_volatility_kmeans_isolated_peak_21d', {})
class Factor_intraday_volatility_kmeans_isolated_peak_21d(MinuteFactor):
    name = 'intraday_volatility_kmeans_isolated_peak_21d'
    description = '结合五类日内波动估计，以当日无监督聚类识别相对高低波动状态，统计孤立高波动时点的出现频率。聚类标签只作中间选择，最终输出多日数量强度。 原文：[邪修成功！我计算了五种波动率，然后用k-means将其聚类后，得到波谷分钟数因子！](https://zhuanlan.zhihu.com/p/2028233293938607143)。'
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
