"""return_centroid_entropy_weighted_regression_21d。

r_m=stock_minute.close[m]/stock_minute.open[m]-1; U={m:r_m>0}; D={m:r_m<0}; a_m=abs(stock_minute.close[m]/stock_minute.close[m-1]-1); h_m=-a_m*ln(a_m+1e-10); h=(h-Min_day(h))/(Max_day(h)-Min_day(h)+1e-10); w=h*stock_minute.vol; Gu=Sum(m*w_m,m in U)/Sum(w_m,m in U); Gd=Sum(m*w_m,m in D)/Sum(w_m,m in D); Hday=Mean_day(h); e_t=Gd_t-Predict(WLS(Gd~1+Gu,weights=1/(Hday+0.1),previous 20d),current t); F=-M20(e)*(2-M5(Hday))
将日内上涨、下跌的时间重心作个股历史回归，研究收益变动局部熵贡献所加权的交易时间分布；与已实现的当日截面回归重心偏离区分。 原文：[(2025.7.3)✅【研报复现】开源证券：日内分钟收益率的时序特征-逻辑讨论与因子增强](https://zhuanlan.zhihu.com/p/2055255505602450466)。
分钟按交易时钟1..240，至少200有效分钟且上下组各至少5点；回归训练仅用t−20..t−1已结束20日，至少15有效日且满秩，预测当日重心后形成残差，低频均值至少17/20日。来源文章把当日最终值回填全部日内bar，本报告只在收盘后生成日值、下一日使用。h按源码为abs收益的−a log a项再日内极差归一，不称作已归一概率的香农熵。收盘比收益不跨交易日，第一分钟缺失；极差0或一侧权重和0缺失，历史WLS只含过去日期。"""
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
MINUTE_INPUTS = {'open': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'open', date_column='trade_time'), 'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time'), 'vol': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'vol', date_column='trade_time')}
FORMULA = 'r_m=stock_minute.close[m]/stock_minute.open[m]-1; U={m:r_m>0}; D={m:r_m<0}; a_m=abs(stock_minute.close[m]/stock_minute.close[m-1]-1); h_m=-a_m*ln(a_m+1e-10); h=(h-Min_day(h))/(Max_day(h)-Min_day(h)+1e-10); w=h*stock_minute.vol; Gu=Sum(m*w_m,m in U)/Sum(w_m,m in U); Gd=Sum(m*w_m,m in D)/Sum(w_m,m in D); Hday=Mean_day(h); e_t=Gd_t-Predict(WLS(Gd~1+Gu,weights=1/(Hday+0.1),previous 20d),current t); F=-M20(e)*(2-M5(Hday))'
RECIPE = {'family': 'return_centroid', 'variant': 'entropy', 'window': 21, 'min_days': 17}

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

def rolling(x, n, method='mean', ddof=0):
    n = int(n)
    if n < 1:
        raise ValueError('滚动窗口必须为正整数')
    roll = x.rolling(n, min_periods=n)
    if method in ('std', 'var'):
        return getattr(roll, method)(ddof=ddof)
    return getattr(roll, method)()

def centroid_result(recipe, p, ctx):
    (gu, gd, ex) = (p['gu'], p['gd'], p['extra'])
    variant = recipe['variant']
    error = gd * np.nan
    for s in gd:
        for t in range(20, len(gd)):
            y = gd[s].iloc[t - 20:t].to_numpy()
            u = gu[s].iloc[t - 20:t].to_numpy()
            xs = [u]
            cur = [1, gu[s].iloc[t]]
            a = np.column_stack([np.ones(20), *xs])
            cur = np.asarray(cur)
            weights = 1 / (ex[s].iloc[t - 20:t].to_numpy() + 0.1)
            good = np.isfinite(y) & np.isfinite(a).all(axis=1) & np.isfinite(weights) & (weights > 0)
            if good.sum() < 15 or not (np.isfinite(cur).all() and np.isfinite(gd[s].iloc[t])):
                continue
            (a, y, weights) = (a[good], y[good], weights[good])
            if np.linalg.matrix_rank(a) < a.shape[1]:
                continue
            w = np.sqrt(weights)
            b = np.linalg.lstsq(a * w[:, None], y * w, rcond=None)[0]
            error.at[gd.index[t], s] = gd[s].iloc[t] - cur @ b
    result = -error.rolling(20, min_periods=17).mean()
    result.iloc[:39] = np.nan
    result *= 2 - rolling(ex, 5)
    return result

def div(a, b):
    if isinstance(b, (pd.DataFrame, pd.Series)):
        b = b.where(np.isfinite(b) & b.ne(0))
    elif np.ndim(b):
        b = np.where(np.isfinite(b) & (b != 0), b, np.nan)
    elif not np.isfinite(b) or b == 0:
        b = np.nan
    with np.errstate(all='ignore'):
        return finite(a / b)

def log(x, base=np.e, offset=0):
    z = x + offset
    if isinstance(z, (pd.DataFrame, pd.Series)):
        z = z.where(z > 0)
    else:
        z = np.where(z > 0, z, np.nan)
    return np.log(z) / np.log(base)

def centroid_features(recipe, ctx, k, p):
    (c, o, v) = (p['close'], p['open'], p.get('vol'))
    r = div(c, o) - 1
    time = pd.Series(np.arange(1, 241, dtype=float), index=c.index)
    variant = recipe['variant']
    up = r > 0
    down = r < 0
    extra = r * 0 + 1
    z = abs(div(c, c.shift(1)) - 1)
    hh = -z * log(z + 1e-10)
    extra = div(hh - hh.min(), hh.max() - hh.min() + 1e-10)
    w = extra * v
    gu = div(w.mul(time, axis=0).where(up).sum(min_count=1), w.where(up).sum(min_count=1))
    gd = div(w.mul(time, axis=0).where(down).sum(min_count=1), w.where(down).sum(min_count=1))
    valid = r.count().ge(200) & up.sum().ge(5) & down.sum().ge(5)
    gu = gu.where(valid)
    gd = gd.where(valid)
    return {'gu': gu, 'gd': gd, 'extra': extra.mean()}

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
    return centroid_features(recipe, ctx, k, p)

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
    return centroid_result(recipe, panels, ctx)

@register_factor
@fixed_factor('return_centroid_entropy_weighted_regression_21d', {})
class Factor_return_centroid_entropy_weighted_regression_21d(MinuteFactor):
    name = 'return_centroid_entropy_weighted_regression_21d'
    description = '将日内上涨、下跌的时间重心作个股历史回归，研究收益变动局部熵贡献所加权的交易时间分布；与已实现的当日截面回归重心偏离区分。 原文：[(2025.7.3)✅【研报复现】开源证券：日内分钟收益率的时序特征-逻辑讨论与因子增强](https://zhuanlan.zhihu.com/p/2055255505602450466)。'
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
