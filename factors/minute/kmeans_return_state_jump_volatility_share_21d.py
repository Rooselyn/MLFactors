"""kmeans_return_state_jump_volatility_share_21d。

r_m=stock_minute.close[m]/stock_minute.close[m-1]-1; v_m=stock_minute.vol[m]/stock_minute.vol[m-1]-1; a_m=stock_minute.amount[m]/stock_minute.amount[m-1]-1; labels=KMeans2(Zscore_day(Clip1_99_day([r_m,v_m,a_m]))); J=smaller cluster; Q=other cluster; D=Std(r in J)/Std(r); F=M21(D); raw returns/volume/amount retained for outputs; at least200 valid minutes, each cluster at least5; 21day aggregation at least17 valid days
用交易状态分域后衡量跳价期波动相对全天波动，区分稀疏异常交易与常规交易中的风险结构；标签不是最终排序输出。 原文：[一个K-means+波动率，居然可以衍生出成百上千个因子！](https://zhuanlan.zhihu.com/p/1890089713681032984)。
分组明确沿前篇公开K-means定义：收益、成交量变化率、成交额变化率三维，不把后篇无代码的标签擅自换成GMM。三列先按本地修订缩尾和标准化，统计输出仍使用原始变化率；收益和变化不跨日，前值量额须正，至少200有效点，两组各至少5点。KMeans补为欧氏距离、k-means++、n_init=10、random_state=0、max_iter=300、tol=1e-4，取平方误差最小的收敛解；少数簇称“跳价期”，只是模型状态而非真实价格跳跃检验，多数簇称“震荡期”。等规模时以收益样本标准差更大者为J，再相等按收益中心大小定序；中心重合缺失。所有Std用ddof=1，方向半偏差以全簇样本归一，已知无该方向收益取0、比率分母正；月度口径统一21日均值、至少17日，不把文中未实际定义的残差、窗口或跳跃扩展全部枚举。本地修订上/下行波动率为簇内半偏差，不再使用方向子样本均值中心化的条件标准差；其与簇内样本标准差之比不保证和为1。
2026-11-06修订：本地覆盖修订：三维变化率先逐股逐日按1%/99%缩尾，再以总体标准差逐列标准化后KMeans；常数列置0。输出仍用原始收益及量额，簇至少5点、每日至少200有效点、21日均值至少17日保持。方向波动改为簇内半偏差sqrt(mean(r^2*I(sign)))，以全簇样本数归一，已知无该方向收益取0，不以缺失代替。"""
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
MINUTE_INPUTS = {'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time'), 'vol': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'vol', date_column='trade_time'), 'amount': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'amount', date_column='trade_time')}
FORMULA = 'r_m=stock_minute.close[m]/stock_minute.close[m-1]-1; v_m=stock_minute.vol[m]/stock_minute.vol[m-1]-1; a_m=stock_minute.amount[m]/stock_minute.amount[m-1]-1; labels=KMeans2(Zscore_day(Clip1_99_day([r_m,v_m,a_m]))); J=smaller cluster; Q=other cluster; D=Std(r in J)/Std(r); F=M21(D); raw returns/volume/amount retained for outputs; at least200 valid minutes, each cluster at least5; 21day aggregation at least17 valid days'
RECIPE = {'family': 'return_kmeans', 'variant': 'jump_volatility_share', 'window': 21, 'min_days': 17}

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
    vol = None
    for s in ctx.symbols:
        features = pd.DataFrame({'r': r[s], 'v': div(v[s], v[s].shift(1)) - 1, 'a': div(a[s], a[s].shift(1)) - 1})
        good = np.isfinite(features).all(axis=1)
        if good.sum() < 200:
            continue
        x = features.loc[good].to_numpy()
        # Local robust state definition: suppress scale and isolated volume-ratio spikes.
        lower, upper = np.quantile(x, [0.01, 0.99], axis=0)
        clipped = np.clip(x, lower, upper)
        scale = clipped.std(axis=0)
        standardized = (clipped - clipped.mean(axis=0)) / np.where(scale > 0, scale, 1.0)
        model = KMeans(n_clusters=2, n_init=10, random_state=0, max_iter=300, tol=0.0001).fit(standardized)
        labels = model.labels_
        counts = np.bincount(labels, minlength=2)
        if counts.min() < 5 or model.n_iter_ >= 300 or np.max(abs(model.cluster_centers_[0] - model.cluster_centers_[1])) <= 1e-12:
            continue
        order = sorted(range(2), key=lambda j: (counts[j], -np.std(x[labels == j, 0], ddof=1), -model.cluster_centers_[j, 0]))
        (jump, quiet) = order
        group = jump
        mask = labels == group
        rr = x[:, 0]
        chosen = rr[mask]
        all_sd = rr.std(ddof=1)
        sd = lambda z: np.std(z, ddof=1) if len(z) >= 3 else np.nan
        prefix = variant.split('_', 1)[1]
        if prefix == 'volatility':
            result = sd(chosen)
        elif prefix == 'volatility_share':
            result = div(sd(chosen), all_sd)
        elif prefix == 'quiet_asymmetry':
            result = div(sd(rr[labels == jump]) - sd(rr[labels == quiet]), all_sd)
        elif prefix == 'up_volatility':
            result = np.sqrt(np.mean(np.where(chosen > 0, chosen * chosen, 0.0)))
        elif prefix == 'up_share':
            result = div(np.sqrt(np.mean(np.where(chosen > 0, chosen * chosen, 0.0))), sd(chosen))
        elif prefix == 'down_volatility':
            result = np.sqrt(np.mean(np.where(chosen < 0, chosen * chosen, 0.0)))
        elif prefix == 'down_share':
            result = div(np.sqrt(np.mean(np.where(chosen < 0, chosen * chosen, 0.0))), sd(chosen))
        elif prefix == 'up_down_asymmetry':
            result = div(np.sqrt(np.mean(np.where(chosen > 0, chosen * chosen, 0.0))) - np.sqrt(np.mean(np.where(chosen < 0, chosen * chosen, 0.0))), sd(chosen))
        elif prefix in ('volume_dispersion', 'amount_dispersion'):
            source = v if prefix.startswith('volume') else a
            result = sd(source.loc[good, s].to_numpy()[mask])
        elif prefix in ('volume_share', 'amount_share'):
            source = v if prefix.startswith('volume') else a
            values = source.loc[good, s].to_numpy()
            result = div(values[mask].sum(), values.sum())
        elif prefix.startswith('vwap_'):
            vv = v.loc[good, s].to_numpy()
            aa = a.loc[good, s].to_numpy()
            vwap[s] = div(aa[mask].sum(), vv[mask].sum())
            all_vwap[s] = div(aa.sum(), vv.sum())
            continue
        else:
            raise ValueError(f'未知KMeans输出: {variant}')
        out[s] = result
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
@fixed_factor('kmeans_return_state_jump_volatility_share_21d', {})
class Factor_kmeans_return_state_jump_volatility_share_21d(MinuteFactor):
    name = 'kmeans_return_state_jump_volatility_share_21d'
    description = '用交易状态分域后衡量跳价期波动相对全天波动，区分稀疏异常交易与常规交易中的风险结构；标签不是最终排序输出。 原文：[一个K-means+波动率，居然可以衍生出成百上千个因子！](https://zhuanlan.zhihu.com/p/1890089713681032984)。 本地修订（2026-11-06）：本地覆盖修订：三维变化率先逐股逐日按1%/99%缩尾，再以总体标准差逐列标准化后KMeans；常数列置0。输出仍用原始收益及量额，簇至少5点、每日至少200有效点、21日均值至少17日保持。方向波动改为簇内半偏差sqrt(mean(r^2*I(sign)))，以全簇样本数归一，已知无该方向收益取0，不以缺失代替。'
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
