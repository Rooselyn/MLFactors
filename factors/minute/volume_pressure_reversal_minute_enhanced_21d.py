"""volume_pressure_reversal_minute_enhanced_21d。

r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; v=ln(stock_day.vol/M60(stock_day.vol)); clv=(2*stock_day.close_hfq-stock_day.high_hfq-stock_day.low_hfq)/(stock_day.high_hfq-stock_day.low_hfq); A=M21(I(r<0)*(-r)*max(v,0)*max(clv,0)); B=M21(I(r>0)*r*max(v,0)*max(clv,0)); C=-(stock_day.close_hfq/L21(stock_day.close_hfq)-1); D=M21(abs(r)/ln(1+1000*stock_day.amount)); E=SD21(r)+M21((stock_day.high_hfq-stock_day.low_hfq)/L1(stock_day.close_hfq)); VPR=0.35*CSZ(A)-0.30*CSZ(B)+0.25*CSZ(C)-0.06*CSZ(D)-0.04*CSZ(E); u_m=stock_minute.vol[d,m]/Median(stock_minute.vol[s,m],s=d-20..d-1); x_m=stock_minute.close[m]/stock_minute.close[m-1]-1; Ct=Last_day(stock_minute.close); SS_d=Sum(I(x<0 and u>1.5)*(-x)*u*(Ct/stock_minute.close-1)); BC_d=Sum(I(x>0 and u>1.5)*x*u*(stock_minute.close/Ct-1)); SS=M21(SS_d); BC=M21(BC_d); F=0.75*VPR+0.25*CSZ(SS-BC)
研究进一步结合盘中卖压修复和追涨后回落的组合；输出连续综合强度，不作为条件选股信号。 原文：[让codex用gpt5.5生成一个大A的量价因子，结果让人哭笑不得！](https://zhuanlan.zhihu.com/p/2055768452439324420)。
日线价格按已有后复权字段，金额千元乘1000转元后取log，vol/M60同单位可消去手数。所有滚动完整、量价分母正、H>L，CSZ在当日共同有效股票上至少100股且方差正；均值/SD按样本窗口。分钟同钟点量中位数只用前20交易日，分钟收益按公式选择相邻收盘、不跨日，全部事件及日末价格在当天盘后可见。源码存在buy_schase/repair未定义变量、买追项与正文符号冲突及10日反转正负冲突，按明确给出的构造公式统一为BC=上行冲击×盘中价/日末价−1、10日收益取负；原始crowdedup_5按实际代码的5日均值，不按文字Sum5。日内至少200完整点，前20日各钟点量完整，SS/BC历史21日均值完整，事件空组为已知0，不填未知分钟。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from collections import OrderedDict
import numpy as np
import pandas as pd
from factors.base import eligibility
import warnings
from factors.base import MinuteFactor
from factors.inputs import read_inputs
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'high_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'high_hfq'), 'low_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'low_hfq'), 'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'), 'amount': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'amount')}
MINUTE_INPUTS = {'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time'), 'open': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'open', date_column='trade_time'), 'high': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'high', date_column='trade_time'), 'low': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'low', date_column='trade_time'), 'vol': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'vol', date_column='trade_time'), 'amount': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'amount', date_column='trade_time')}
FORMULA = 'r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; v=ln(stock_day.vol/M60(stock_day.vol)); clv=(2*stock_day.close_hfq-stock_day.high_hfq-stock_day.low_hfq)/(stock_day.high_hfq-stock_day.low_hfq); A=M21(I(r<0)*(-r)*max(v,0)*max(clv,0)); B=M21(I(r>0)*r*max(v,0)*max(clv,0)); C=-(stock_day.close_hfq/L21(stock_day.close_hfq)-1); D=M21(abs(r)/ln(1+1000*stock_day.amount)); E=SD21(r)+M21((stock_day.high_hfq-stock_day.low_hfq)/L1(stock_day.close_hfq)); VPR=0.35*CSZ(A)-0.30*CSZ(B)+0.25*CSZ(C)-0.06*CSZ(D)-0.04*CSZ(E); u_m=stock_minute.vol[d,m]/Median(stock_minute.vol[s,m],s=d-20..d-1); x_m=stock_minute.close[m]/stock_minute.close[m-1]-1; Ct=Last_day(stock_minute.close); SS_d=Sum(I(x<0 and u>1.5)*(-x)*u*(Ct/stock_minute.close-1)); BC_d=Sum(I(x>0 and u>1.5)*x*u*(stock_minute.close/Ct-1)); SS=M21(SS_d); BC=M21(BC_d); F=0.75*VPR+0.25*CSZ(SS-BC)'
RECIPE = {'family': 'volume_pressure', 'variant': 'enhanced', 'window': 21, 'min_days': 21}

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

def div(a, b):
    if isinstance(b, (pd.DataFrame, pd.Series)):
        b = b.where(np.isfinite(b) & b.ne(0))
    elif np.ndim(b):
        b = np.where(np.isfinite(b) & (b != 0), b, np.nan)
    elif not np.isfinite(b) or b == 0:
        b = np.nan
    with np.errstate(all='ignore'):
        return finite(a / b)

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

    def clock(self, f, k, n=21, method='z', minimum=None, prior=False):
        minimum = n if minimum is None else minimum
        end = k if prior else k + 1
        start = max(0, end - n)
        if end - start < minimum:
            return self.day(k)[f] * np.nan
        a = self.cubes[f][start:end]
        count = np.isfinite(a).sum(axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            mean = np.nanmean(a, axis=0)
            sd = np.nanstd(a, axis=0, ddof=1)
            med = np.nanmedian(a, axis=0)
            value = mean if method == 'mean' else med if method == 'median' else np.nanmedian(abs(a - med), axis=0) if method == 'mad' else div(self.cubes[f][k] - mean, sd)
        return pd.DataFrame(np.where(count >= minimum, value, np.nan), index=grid(self.days[k]), columns=self.symbols)

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
    hist = ctx.clock('vol', k, n=20, method='median', prior=True)
    relative = div(v, hist)
    last = c.iloc[-1]
    sell = r.lt(0) & relative.gt(1.5)
    buy = r.gt(0) & relative.gt(1.5)
    ss = (-r * relative * (div(last, c) - 1) * sell.astype(float)).sum(min_count=200)
    bc = (r * relative * (div(c, last) - 1) * buy.astype(float)).sum(min_count=200)
    good = hist.notna().sum().eq(240)
    return {'ss': ss.where(good), 'bc': bc.where(good)}

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

def log(x, base=np.e, offset=0):
    z = x + offset
    if isinstance(z, (pd.DataFrame, pd.Series)):
        z = z.where(z > 0)
    else:
        z = np.where(z > 0, z, np.nan)
    return np.log(z) / np.log(base)

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

def volume_pressure_result(recipe, p, ctx):
    v = ctx.v
    r = div(v['close_hfq'], v['close_hfq'].shift(1)) - 1
    vol = log(div(v['vol'], rolling(v['vol'], 60)))
    clv = div(2 * v['close_hfq'] - v['high_hfq'] - v['low_hfq'], v['high_hfq'] - v['low_hfq'])
    days = ctx.days
    ill = rolling(div(abs(r), log(1 + 1000 * v['amount'])), 21)
    z = lambda x: zscore(x, 0, ctx.e).where(x.where(ctx.e).count(axis=1) >= 100, axis=0)
    vpr = 0.35 * z(rolling((r < 0).astype(float) * -r * np.maximum(vol, 0) * np.maximum(clv, 0), 21)) - 0.3 * z(rolling((r > 0).astype(float) * r * np.maximum(vol, 0) * np.maximum(clv, 0), 21)) + 0.25 * z(-(div(v['close_hfq'], v['close_hfq'].shift(21)) - 1)) - 0.06 * z(ill) - 0.04 * z(rolling(r, 21, 'std') + rolling(div(v['high_hfq'] - v['low_hfq'], v['close_hfq'].shift(1)), 21))
    ss = rolling(p['ss'], 21).reindex(ctx.dates)
    bc = rolling(p['bc'], 21).reindex(ctx.dates)
    return (0.75 * vpr + 0.25 * z(ss - bc)).reindex(days)

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
    return volume_pressure_result(recipe, panels, ctx)

@register_factor
@fixed_factor('volume_pressure_reversal_minute_enhanced_21d', {})
class Factor_volume_pressure_reversal_minute_enhanced_21d(MinuteFactor):
    name = 'volume_pressure_reversal_minute_enhanced_21d'
    description = '研究进一步结合盘中卖压修复和追涨后回落的组合；输出连续综合强度，不作为条件选股信号。 原文：[让codex用gpt5.5生成一个大A的量价因子，结果让人哭笑不得！](https://zhuanlan.zhihu.com/p/2055768452439324420)。'
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
