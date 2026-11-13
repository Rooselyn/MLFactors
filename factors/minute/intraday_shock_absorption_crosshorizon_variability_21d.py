"""intraday_shock_absorption_crosshorizon_variability_21d。

r_m=ln(stock_minute.close[m]/stock_minute.close[m-1]); M_m=CSMedian(r_m); a_m=r_m-M_m; sigma=1.4826*Median_day(abs(a-Median_day(a))); R_m=stock_minute.high-stock_minute.low+1e-8*stock_minute.close; W_m=stock_minute.amount/stock_minute.vol; S_m=(clip(a_m/(3*max(sigma,1e-8)),-1,1)+(stock_minute.close-stock_minute.open)/R_m+(2*stock_minute.close-stock_minute.high-stock_minute.low)/R_m+clip(2*(stock_minute.close-W_m)/R_m,-1,1))/4; z_m=(ln(1+stock_minute.amount[d,m])-Median_s(ln(1+stock_minute.amount[s,m])))/(1.4826*MAD_s(ln(1+stock_minute.amount[s,m]))+1e-8),s=d-20..d-1; w_m=max(z_m-1,0)*abs(S_m); g_K,m=ln(stock_minute.close[m+K]/stock_minute.close[m])-Sum(M_u,u=m+1..m+K); h_K,m=g_K,m-Median_session(g_K); X_K,pos=Sum(w*h_K with S>0)/(3+Sum(w with S>0)); X_K,neg=Sum(w*h_K with S<0)/(3+Sum(w with S<0)); Q=Mean(NormalRank(X_5,pos),NormalRank(X_5,neg),NormalRank(X_20,pos),NormalRank(X_20,neg)); F=SD21(Q,min_periods=17,ddof=0); clock median/MAD over previous20 days min16 known days; current data min200 minutes; no observed directional shock contributes0 only on valid data; horizons5/20 min180/160 valid pairs
衡量异常成交额和方向清晰的价格冲击之后、同一交易时段内延续或修复强度的跨日变化，研究承接信息的不稳定性。 原文：[让codex用gpt5.6Extra High来模仿金工诗人曹春晓老师，复杂度让人窒息！](https://zhuanlan.zhihu.com/p/2063016131112219564)。
按正文与代码主结构完整展开：每半日剔除首5和末5分钟，K步必须全部位于同一上午/下午内；市场中位数每分钟至少100股。未来K分钟仅相对于当日盘中起点，仍在信号日收盘前，最终为盘后因子，严禁在起点分钟提前使用。价格/量分母须正，同钟点前20日历史金额完整；EPS原文未给值补1e-8，lambda代码为3。每个K与方向至少3有效事件，无事件不靠lambda生成伪零；NormalRank=Phi_inverse((平均秩−0.5)/N)、N>=100，四支齐全等权后须21个有效Q。只计原文最终组合，未将两个K的组件复制为四个新因子。
2026-11-06修订：按披露公式纠正分钟收益为对数收益；完整当前日与前20日同钟金额已知时，某方向没有异常成交冲击的收缩贡献定义为0（分母原有+3保持），不再要求至少3个稀有事件。缺历史、缺当前行情或缺有效未来分钟仍缺失；两档持有期仅使用当日已收盘分钟，随后21日波动保持完整窗口。 稀疏异常分钟不再令全日作废：当前各字段至少200有效分钟，前20日同钟统计至少16日且至少200个有效时钟；5/20分钟持有期分别至少180/160对有效观测。历史中位数和MAD仅用已知值；外层21日总体标准差至少17日。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from collections import OrderedDict
import numpy as np
import pandas as pd
from factors.base import eligibility
from factors.base import MinuteFactor
import warnings
from scipy import stats
from factors.inputs import read_inputs
INPUTS = {}
MINUTE_INPUTS = {'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time'), 'open': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'open', date_column='trade_time'), 'high': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'high', date_column='trade_time'), 'low': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'low', date_column='trade_time'), 'vol': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'vol', date_column='trade_time'), 'amount': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'amount', date_column='trade_time')}
FORMULA = 'r_m=ln(stock_minute.close[m]/stock_minute.close[m-1]); M_m=CSMedian(r_m); a_m=r_m-M_m; sigma=1.4826*Median_day(abs(a-Median_day(a))); R_m=stock_minute.high-stock_minute.low+1e-8*stock_minute.close; W_m=stock_minute.amount/stock_minute.vol; S_m=(clip(a_m/(3*max(sigma,1e-8)),-1,1)+(stock_minute.close-stock_minute.open)/R_m+(2*stock_minute.close-stock_minute.high-stock_minute.low)/R_m+clip(2*(stock_minute.close-W_m)/R_m,-1,1))/4; z_m=(ln(1+stock_minute.amount[d,m])-Median_s(ln(1+stock_minute.amount[s,m])))/(1.4826*MAD_s(ln(1+stock_minute.amount[s,m]))+1e-8),s=d-20..d-1; w_m=max(z_m-1,0)*abs(S_m); g_K,m=ln(stock_minute.close[m+K]/stock_minute.close[m])-Sum(M_u,u=m+1..m+K); h_K,m=g_K,m-Median_session(g_K); X_K,pos=Sum(w*h_K with S>0)/(3+Sum(w with S>0)); X_K,neg=Sum(w*h_K with S<0)/(3+Sum(w with S<0)); Q=Mean(NormalRank(X_5,pos),NormalRank(X_5,neg),NormalRank(X_20,pos),NormalRank(X_20,neg)); F=SD21(Q,min_periods=17,ddof=0); clock median/MAD over previous20 days min16 known days; current data min200 minutes; no observed directional shock contributes0 only on valid data; horizons5/20 min180/160 valid pairs'
RECIPE = {'family': 'shock_absorption', 'window': 21, 'min_days': 17, 'aggregation': 'std'}

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
    r = np.log(div(c, c.shift(1))) if c is not None else None
    market = r.median(axis=1)
    centered = r.sub(market, axis=0)
    sigma = 1.4826 * (centered - centered.median()).abs().median()
    ranges = h - l + 1e-08 * c
    w = div(a, v)
    sentiment = (div(centered, 3 * np.maximum(sigma, 1e-08)).clip(-1, 1) + div(c - o, ranges) + div(2 * c - h - l, ranges) + div(2 * (c - w), ranges).clip(-1, 1)) / 4
    if k < 20:
        return {key: nan.copy() for key in ('up5', 'down5', 'up20', 'down20')}
    previous = np.stack([log(1 + ctx.day(i)['amount']).to_numpy() for i in range(k - 20, k)])
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        med = np.nanmedian(previous, axis=0)
        mad = np.nanmedian(abs(previous - med), axis=0)
    clock_known = np.isfinite(previous).sum(axis=0) >= 16
    med = np.where(clock_known, med, np.nan)
    mad = np.where(clock_known, mad, np.nan)
    z = div(log(1 + a) - med, 1.4826 * mad + 1e-08)
    weight = np.maximum(z - 1, 0) * abs(sentiment)
    known_history = clock_known.sum(axis=0) >= 200
    known_day = np.logical_and.reduce([np.isfinite(x.to_numpy()).sum(axis=0) >= 200 for x in p.values()])
    result = {}
    for horizon in (5, 20):
        future = log(div(c.shift(-horizon), c))
        marketfuture = pd.Series(np.nan, index=c.index)
        for i in range(240 - horizon):
            if i < 120 <= i + horizon:
                continue
            marketfuture.iloc[i] = market.iloc[i + 1:i + horizon + 1].sum(min_count=horizon)
        excess = future.sub(marketfuture, axis=0)
        session = pd.Series(np.r_[np.zeros(120), np.ones(120)], index=c.index)
        excess = excess - excess.groupby(session).transform('median')
        for direction in ('up', 'down'):
            selected = sentiment.gt(0) if direction == 'up' else sentiment.lt(0)
            selected &= excess.notna() & weight.gt(0)
            count = selected.sum()
            # The existing +3 shrinkage defines a zero contribution when no event was observed.
            value = div((weight * excess).where(selected, 0.0).sum(), 3 + weight.where(selected, 0.0).sum())
            known_pairs = (excess.notna() & weight.notna() & sentiment.notna()).sum()
            result[direction + str(horizon)] = value.where(known_day & known_history & known_pairs.ge(180 if horizon == 5 else 160))
    return result

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
    ee = ctx.e.reindex(ctx.days)
    qs = []
    for key in ('up5', 'down5', 'up20', 'down20'):
        x = panels[key].where(ee)
        n = x.count(axis=1)
        q = div(x.rank(axis=1, method='average') - 0.5, n.to_numpy()[:, None])
        qs.append(pd.DataFrame(stats.norm.ppf(q), index=x.index, columns=x.columns).where(n >= 100, axis=0))
    panel = sum(qs) / 4
    return aggregate_features(panel, recipe)

@register_factor
@fixed_factor('intraday_shock_absorption_crosshorizon_variability_21d', {})
class Factor_intraday_shock_absorption_crosshorizon_variability_21d(MinuteFactor):
    name = 'intraday_shock_absorption_crosshorizon_variability_21d'
    description = '衡量异常成交额和方向清晰的价格冲击之后、同一交易时段内延续或修复强度的跨日变化，研究承接信息的不稳定性。 原文：[让codex用gpt5.6Extra High来模仿金工诗人曹春晓老师，复杂度让人窒息！](https://zhuanlan.zhihu.com/p/2063016131112219564)。 本地修订（2026-11-06）：按披露公式纠正分钟收益为对数收益；完整当前日与前20日同钟金额已知时，某方向没有异常成交冲击的收缩贡献定义为0（分母原有+3保持），不再要求至少3个稀有事件。缺历史、缺当前行情或缺有效未来分钟仍缺失；两档持有期仅使用当日已收盘分钟，随后21日波动保持完整窗口。 稀疏异常分钟不再令全日作废：当前各字段至少200有效分钟，前20日同钟统计至少16日且至少200个有效时钟；5/20分钟持有期分别至少180/160对有效观测。历史中位数和MAD仅用已知值；外层21日总体标准差至少17日。'
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
