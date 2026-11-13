"""residual_return_noise_mmd_21d。

P_d,m=stock_minute.close[d,m]*stock_day.adj_factor[d]; r= P/LagTradingMinute(P)-1 over last 21 days; M=CSMean(r); e21=OLSResidual(r_i~1+M,all 21-day minutes); e1=OLSResidual(r_i~1+M,current day minutes); x=LastDay(e21/Std(e21,ddof=1)); y=e1/Std(e1,ddof=1); K(a,b)=exp(-(a-b)^2); D=Mean(K(x,x))+Mean(K(y,y))-2*Mean(K(x,y)); F=M21(D)
比较同一日收益在近月市场模型与当日市场模型下标准化残差的分布差异，研究个股独立噪声结构的变化。 原文：[残差收益噪声偏离，分层回测效果炸裂！这应该算独创性因子了吧！](https://zhuanlan.zhihu.com/p/2018441534136131774)。
两个模型各自含截距、各用自身整段残差样本标准差，x只取当日对应点而非全部5040个历史点；同一当前分钟网格上比较。历史模型至少4000个有效点、当前至少200点，市场截面至少100股，两残差方差正；逐日用对应adj_factor而非错误重复当前一行复权因子，保留跨交易分钟收益中的隔夜项，不填缺失。RBF gamma=1，包含对角项，21日至少17日；移除作者特定历史样本截止日，不使用未知样本外记录。"""
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
INPUTS = {'adj_factor': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'adj_factor')}
MINUTE_INPUTS = {'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time')}
FORMULA = 'P_d,m=stock_minute.close[d,m]*stock_day.adj_factor[d]; r= P/LagTradingMinute(P)-1 over last 21 days; M=CSMean(r); e21=OLSResidual(r_i~1+M,all 21-day minutes); e1=OLSResidual(r_i~1+M,current day minutes); x=LastDay(e21/Std(e21,ddof=1)); y=e1/Std(e1,ddof=1); K(a,b)=exp(-(a-b)^2); D=Mean(K(x,x))+Mean(K(y,y))-2*Mean(K(x,y)); F=M21(D)'
RECIPE = {'family': 'residual_noise', 'window': 21, 'min_days': 17}

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

def mmd(a, b):
    (a, b) = (np.asarray(a, float), np.asarray(b, float))
    (a, b) = (a[np.isfinite(a)], b[np.isfinite(b)])
    if not len(a) or not len(b):
        return np.nan
    return np.exp(-(a[:, None] - a[None, :]) ** 2).mean() + np.exp(-(b[:, None] - b[None, :]) ** 2).mean() - 2 * np.exp(-(a[:, None] - b[None, :]) ** 2).mean()

def fit(y, xs, minimum=3, intercept=True, kind='residual', weights=None):
    """同一天的列分别回归；标准化解释量再求解以避免量纲造成伪秩不足。"""
    yy = y.to_numpy(float)
    xx = np.column_stack([x.to_numpy(float) for x in xs])
    ok = np.isfinite(yy) & np.isfinite(xx).all(axis=1)
    if weights is not None:
        ok &= np.isfinite(weights) & (weights > 0)
    if ok.sum() < max(minimum, len(xs) + int(intercept)):
        return None
    a = xx[ok]
    scale = np.sqrt(np.mean(a * a, axis=0))
    scale[scale == 0] = 1
    a = a / scale
    if intercept:
        a = np.column_stack([np.ones(ok.sum()), a])
    if np.linalg.matrix_rank(a) < a.shape[1]:
        return None
    w = np.sqrt(np.asarray(weights)[ok]) if weights is not None else np.ones(ok.sum())
    beta = np.linalg.lstsq(a * w[:, None], yy[ok] * w, rcond=None)[0]
    res = yy[ok] - a @ beta
    if kind == 'beta':
        return beta / np.r_[1, scale] if intercept else beta / scale
    if kind == 'r2':
        return 1 - div(np.sum(res * res), np.sum((yy[ok] - yy[ok].mean()) ** 2))
    out = pd.Series(np.nan, index=y.index)
    out.iloc[np.flatnonzero(ok)] = res
    return out

def ts_residual(y, xs, minimum=3):
    out = y * np.nan
    for s in y:
        res = fit(y[s], [x[s] if isinstance(x, pd.DataFrame) else x for x in xs], minimum)
        if res is not None:
            out[s] = res
    return out

def window_features(recipe, ctx, k, p):
    family = recipe['family']
    variant = recipe.get('variant', '')
    nan = pd.Series(np.nan, index=ctx.symbols)
    n = 21
    if k < n - 1:
        return {'d': nan}
    start = (k - n + 1) * 240
    stop = (k + 1) * 240
    adj = ctx.v.get('adj_factor')
    adjarr = None
    if adj is not None:
        adjarr = np.repeat(adj.reindex(index=ctx.days, columns=ctx.symbols).iloc[k - n + 1:k + 1].to_numpy(), 240, axis=0)
    close = ctx.p['close'].iloc[start:stop]
    price = close * adjarr if adjarr is not None else close
    allprice = ctx.p['close'] * np.repeat(ctx.v['adj_factor'].reindex(index=ctx.days, columns=ctx.symbols).to_numpy(), 240, axis=0) if adj is not None else ctx.p['close']
    rr = div(allprice, allprice.shift(1)) - 1
    rr = rr.iloc[start:stop]
    out = nan.copy()
    day_r = rr.iloc[-240:]
    market = rr.mean(axis=1).where(rr.count(axis=1) >= 100)
    e21 = ts_residual(rr, [market], 4000)
    e1 = ts_residual(day_r, [market.iloc[-240:]], 200)
    for s in ctx.symbols:
        x = div(e21[s].iloc[-240:], e21[s].std(ddof=1))
        y = div(e1[s], e1[s].std(ddof=1))
        out[s] = mmd(x, y) if x.notna().sum() >= 200 and y.notna().sum() >= 200 else np.nan
    return {'d': out}

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
    return window_features(recipe, ctx, k, p)

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
@fixed_factor('residual_return_noise_mmd_21d', {})
class Factor_residual_return_noise_mmd_21d(MinuteFactor):
    name = 'residual_return_noise_mmd_21d'
    description = '比较同一日收益在近月市场模型与当日市场模型下标准化残差的分布差异，研究个股独立噪声结构的变化。 原文：[残差收益噪声偏离，分层回测效果炸裂！这应该算独创性因子了吧！](https://zhuanlan.zhihu.com/p/2018441534136131774)。'
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
