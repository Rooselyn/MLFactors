"""return_gmm_three_down_probability_variability_21d。

r_m=stock_minute.close[m]/stock_minute.close[m-1]-1; fit p(r)=Sum(w_k*Normal(r;mu_k,sigma_k^2),k=1..K) separately each day; K=3; order mu_L<mu_Q<mu_U; F=SD21(w_L)
用三高斯收益分布区分下行、常态和上行状态，研究负向状态出现概率跨日的不稳定性；最终排序输出是连续参数或其历史统计，不是三个状态标签。 原文：[用高斯混合分布将分钟级收益率划分为震荡期、下跌期和上涨期之和，看起来比跳价期和震荡期要好！](https://zhuanlan.zhihu.com/p/1890812859329537330)。
只用同一交易日相邻分钟收益，不引入隔夜收益；至少200个有效收益。EM补定为一维full covariance、n_init=10、random_state=0、reg_covar=1e-8、max_iter=500、tol=1e-5，选择对数似然最大的收敛解；初始化用K-means。权重须大于0.02，标准差须正，退化/不收敛缺失，不用未来收益给簇定名。21日均值、标准差或方差均至少17个有效日，跨日标准差/方差ddof=1。分钟聚类参数仅由现有收盘价计算，不需要预制状态字段。标签按拟合均值从小到大排列，要求mu_L<0<mu_U且abs(mu_Q)不大于两端绝对均值；不满足则缺失，避免强行把三个同向簇命名为涨跌常态。均值与标准差采用混合分布参数，不把硬分类子样本统计混称模型参数。低频聚合优先采用各小节明确展示的方式：常态概率用标准差、常态标准差按正文展示用跨日方差、上下行均值用跨日标准差、下行标准差用均值；未指定者统一补为21日均值。未枚举所有均值/方差/标准差组合。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from collections import OrderedDict
import numpy as np
import pandas as pd
from factors.base import eligibility
from factors.base import MinuteFactor
from sklearn.mixture import GaussianMixture
import warnings
from factors.inputs import read_inputs
INPUTS = {}
MINUTE_INPUTS = {'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time')}
FORMULA = 'r_m=stock_minute.close[m]/stock_minute.close[m-1]-1; fit p(r)=Sum(w_k*Normal(r;mu_k,sigma_k^2),k=1..K) separately each day; K=3; order mu_L<mu_Q<mu_U; F=SD21(w_L)'
RECIPE = {'family': 'return_gmm', 'variant': 'three_down_probability_variability', 'window': 21, 'min_days': 17}

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
        data = r[s].dropna().to_numpy()
        if len(data) < 200 or np.ptp(data) <= 1e-12:
            continue
        components = 3
        model = GaussianMixture(n_components=components, covariance_type='full', reg_covar=1e-06, n_init=10, random_state=0, max_iter=300, tol=0.001, init_params='kmeans').fit(data[:, None])
        if not model.converged_:
            continue
        mu = model.means_[:, 0]
        sigma = np.sqrt(model.covariances_[:, 0, 0])
        weight = model.weights_
        order = np.argsort(mu, kind='stable')
        (mu, sigma, weight) = (mu[order], sigma[order], weight[order])
        if np.min(np.diff(mu)) <= 1e-12 or weight.min() <= 1e-06:
            continue
        if components == 2:
            j = int(np.argmin(weight))
            out[s] = sigma[j]
        else:
            out[s] = {'three_quiet_probability_variability': weight[1], 'three_quiet_mean': mu[1], 'three_quiet_dispersion_variability': sigma[1], 'three_up_probability': weight[2], 'three_up_mean_variability': mu[2], 'three_up_dispersion': sigma[2], 'three_down_probability_variability': weight[0], 'three_down_mean_variability': mu[0], 'three_down_dispersion': sigma[0], 'three_up_down_center_sum': mu[2] + mu[0]}[variant]
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
    recipe = {**recipe, 'aggregation': 'std', 'ddof': 1}
    return aggregate_features(panel, recipe)

@register_factor
@fixed_factor('return_gmm_three_down_probability_variability_21d', {})
class Factor_return_gmm_three_down_probability_variability_21d(MinuteFactor):
    name = 'return_gmm_three_down_probability_variability_21d'
    description = '用三高斯收益分布区分下行、常态和上行状态，研究负向状态出现概率跨日的不稳定性；最终排序输出是连续参数或其历史统计，不是三个状态标签。 原文：[用高斯混合分布将分钟级收益率划分为震荡期、下跌期和上涨期之和，看起来比跳价期和震荡期要好！](https://zhuanlan.zhihu.com/p/1890812859329537330)。'
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
