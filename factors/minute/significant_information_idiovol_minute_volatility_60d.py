"""significant_information_idiovol_minute_volatility_60d。

r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; e=OLSResidual(r~1+FFLocalMKT+FFLocalSMB+FFLocalHML,last60days); S=Top20Days(Std_day(stock_minute.close/stock_minute.open-1,ddof=1),last60days); D=sqrt(Mean(e_s^2,s in S)); F=D
用高分钟波动日筛选信息显著样本，观察剔除市场、规模和价值共同变化后的特有风险。 原文：[显著信息特质波动率，花里胡哨的操作带来的提升肉眼不可见，最后还得靠黑科技！](https://zhuanlan.zhihu.com/p/2048154692660761543)。
采用公开代码对同一60日完整窗口回归后取残差，按选择变量最大的20日取均方根，不对20条再去均值。60日收益、控制组合及排序量均完整，矩阵满秩、残差非退化；并列按交易日期取较近者。FFLocal三控制组合按报告公共定义从本项目行情构造、无风险基准固定0，不调用缺失的官方风格收益字段。分钟波动日需至少200条当根开收盘有效收益。"""
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
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'pb': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pb')}
MINUTE_INPUTS = {'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time'), 'open': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'open', date_column='trade_time')}
FORMULA = 'r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; e=OLSResidual(r~1+FFLocalMKT+FFLocalSMB+FFLocalHML,last60days); S=Top20Days(Std_day(stock_minute.close/stock_minute.open-1,ddof=1),last60days); D=sqrt(Mean(e_s^2,s in S)); F=D'
RECIPE = {'family': 'minute_specific_information', 'window': 60, 'min_days': 60}

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

def ff_local(v, eligible):
    (c, mv, pb) = (v['close_hfq'], v['total_mv'], v['pb'])
    r = div(c, c.shift(1)) - 1
    good = eligible & r.notna() & mv.gt(0) & pb.gt(0)
    controls = {n: r * np.nan for n in ('MKT', 'SMB', 'HML', 'UMD')}
    mom = div(c.shift(21), c.shift(252)) - 1
    for d in r.index:
        ids = r.columns[good.loc[d]]
        if len(ids) < 60:
            continue
        size = mv.loc[d, ids].sort_index().sort_values(kind='stable')
        small = size.index[:len(size) // 2]
        big = size.index[len(size) // 2:]

        def vw(ss):
            w = mv.loc[d, ss]
            return (w * r.loc[d, ss]).sum() / w.sum() if len(ss) else np.nan
        mkt = vw(ids)
        cells = []
        for ss in (small, big):
            bp = div(1, pb.loc[d, ss]).sort_index().sort_values(kind='stable')
            n = len(bp)
            split = (int(np.ceil(0.3 * n)), int(np.ceil(0.7 * n)))
            bins = [bp.index[:split[0]], bp.index[split[0]:split[1]], bp.index[split[1]:]]
            cells.extend((vw(s) if len(s) >= 10 else np.nan for s in bins))
        (sl, sm, sh, bl, bm, bh) = cells
        for (name, x) in [('MKT', mkt), ('SMB', (sl + sm + sh - bl - bm - bh) / 3), ('HML', (sh + bh - sl - bl) / 2)]:
            controls[name].loc[d] = x
        mo = mom.loc[d, ids].dropna().sort_index().sort_values(kind='stable')
        n = int(np.floor(0.3 * len(mo)))
        if n >= 20:
            controls['UMD'].loc[d] = vw(mo.index[-n:]) - vw(mo.index[:n])
    return (r, controls)

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    cached = v.get('_ff_local')
    if cached is None:
        (r, controls) = ff_local(v, e)
    else:
        (full_r, full_controls) = cached
        r = full_r.reindex(index=c.index, columns=c.columns)
        controls = {k: x.reindex(index=c.index, columns=c.columns) for (k, x) in full_controls.items()}
    ff = [controls[k] for k in ('MKT', 'SMB', 'HML', 'UMD')]
    score = v['minute_volatility']
    score = score.reindex(index=c.index, columns=c.columns)
    out = c * np.nan
    base = c * np.nan
    candidates = score.notna().rolling(60, min_periods=60).sum().eq(60).to_numpy()
    for j in range(c.shape[1]):
        yy = r.iloc[:, j].to_numpy()
        xx = np.column_stack([x.iloc[:, j].to_numpy() for x in ff[:3]])
        qq = score.iloc[:, j].to_numpy()
        for t in np.flatnonzero(candidates[:, j]):
            y = yy[t - 59:t + 1]
            xs = xx[t - 59:t + 1]
            q = qq[t - 59:t + 1]
            a = np.column_stack([np.ones(60), xs])
            valid = np.isfinite(y) & np.isfinite(a).all(axis=1) & np.isfinite(q)
            if valid.sum() < 60 or np.linalg.matrix_rank(a) < 4:
                continue
            res = y - a @ np.linalg.lstsq(a, y, rcond=None)[0]
            top = np.lexsort((-np.arange(60), -q))[:20]
            out.iat[t, j] = np.sqrt(np.mean(res[top] ** 2))
            base.iat[t, j] = np.sqrt(np.mean(res ** 2))
    return out

def window_features(recipe, ctx, k, p):
    family = recipe['family']
    variant = recipe.get('variant', '')
    nan = pd.Series(np.nan, index=ctx.symbols)
    return {'d': (div(p['close'], p['open']) - 1).std(ddof=1).where(p['close'].count() >= 200)}

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
    v = dict(ctx.v)
    v['minute_volatility'] = panel.reindex(ctx.dates)
    return compute_daily({'family': 'specific_information', 'variant': 'minute'}, v, ctx.e).reindex(ctx.days)

@register_factor
@fixed_factor('significant_information_idiovol_minute_volatility_60d', {})
class Factor_significant_information_idiovol_minute_volatility_60d(MinuteFactor):
    name = 'significant_information_idiovol_minute_volatility_60d'
    description = '用高分钟波动日筛选信息显著样本，观察剔除市场、规模和价值共同变化后的特有风险。 原文：[显著信息特质波动率，花里胡哨的操作带来的提升肉眼不可见，最后还得靠黑科技！](https://zhuanlan.zhihu.com/p/2048154692660761543)。'
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
        (values, dates, columns) = daily_values(daily_data, self.INPUTS)
        ff_cache = ff_local(values, eligibility(daily_data, dates, columns))
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
