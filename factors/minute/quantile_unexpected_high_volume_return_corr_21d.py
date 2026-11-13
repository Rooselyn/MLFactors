"""quantile_unexpected_high_volume_return_corr_21d。

v_m=stock_minute.vol[m]/Mean_day(stock_minute.vol); r_m=stock_minute.close[m]/stock_minute.open[m]-1; X_m=(1,10000*r_m,v_(m-1),I(first30tradingminutes),I(last30tradingminutes)); b=argmin_b Sum(rho_0.8(v_m-X_m*b)); e=v-X*b; D=Corr_day(e,r); F=M21(D)
在收益、时段和量能延续条件下提取高分位成交量残差，研究异常交易是否偏向价格上涨或承压时刻。 原文：[兴业证券最新研究！ 一个IC和分层超级炸裂的因子诞生了！](https://zhuanlan.zhihu.com/p/2097107862862436306)。
rho_tau(u)=u*(tau-I(u<0))，不加L1/L2系数惩罚，含截距分位数回归可用线性规划HiGHS求解。第1分钟缺同日滞后量剔除，保留午休相邻交易分钟；收益不取绝对值，零量可留、负量或未知量缺失，开收盘须正、日均量正。开收盘哑变量时段按已公开同研报定义取首末30分钟。按来源用全部有效残差与收益相关，不只筛e>0；至少60点、双方方差正、求解失败缺失，21日至少17日。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from collections import OrderedDict
import numpy as np
import pandas as pd
from factors.base import eligibility
from factors.base import MinuteFactor
from scipy import linalg
from scipy import optimize
from scipy import sparse
import warnings
from factors.inputs import read_inputs
INPUTS = {}
MINUTE_INPUTS = {'open': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'open', date_column='trade_time'), 'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time'), 'vol': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'vol', date_column='trade_time')}
FORMULA = 'v_m=stock_minute.vol[m]/Mean_day(stock_minute.vol); r_m=stock_minute.close[m]/stock_minute.open[m]-1; X_m=(1,10000*r_m,v_(m-1),I(first30tradingminutes),I(last30tradingminutes)); b=argmin_b Sum(rho_0.8(v_m-X_m*b)); e=v-X*b; D=Corr_day(e,r); F=M21(D)'
RECIPE = {'family': 'quantile_volume', 'variant': 'return_corr', 'window': 21, 'min_days': 17}

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

def lag(x, n=1, session=False):
    a = x.shift(n)
    if session:
        a.iloc[120:120 + n] = np.nan
    return a

def quantile_fit(y, x, tau, minimum=60, min_norm=False):
    valid = np.isfinite(y) & np.isfinite(x).all(axis=1)
    a = np.asarray(x)[valid]
    b = np.asarray(y)[valid]
    if len(b) < minimum or np.linalg.matrix_rank(a) < a.shape[1]:
        return None
    (n, k) = a.shape
    identity = sparse.eye(n, format='csc')
    equality = sparse.hstack([sparse.csc_matrix(a), identity, -identity], format='csc')
    objective = np.r_[np.zeros(k), np.full(n, tau), np.full(n, 1 - tau)]
    result = optimize.linprog(objective, A_eq=equality, b_eq=b, bounds=[(None, None)] * k + [(0, None)] * (2 * n), method='highs')
    if not result.success:
        return None
    beta = result.x[:k]
    if min_norm:
        dual = result.eqlin.marginals
        tol = 1e-08
        upper = dual >= tau - tol
        lower = dual <= tau - 1 + tol
        interior = ~(upper | lower)
        constraints = []
        eq = a[interior]
        rhs = b[interior]
        if len(eq):
            (_, _, piv) = linalg.qr(eq.T, pivoting=True, mode='economic')
            independent = piv[:np.linalg.matrix_rank(eq)]
            (eq, rhs) = (eq[independent], rhs[independent])
        if len(eq) < k:
            if len(eq):
                constraints.append(optimize.LinearConstraint(eq, rhs, rhs))
            if upper.any():
                constraints.append(optimize.LinearConstraint(a[upper], -np.inf, b[upper]))
            if lower.any():
                constraints.append(optimize.LinearConstraint(a[lower], b[lower], np.inf))
            refined = optimize.minimize(lambda z: 0.5 * (z @ z), beta, jac=lambda z: z, method='SLSQP', constraints=constraints, options={'maxiter': 300, 'ftol': 1e-10})
            if not refined.success:
                return None
            beta = refined.x
        residual = b - a @ beta
        loss = np.sum(np.where(residual >= 0, tau * residual, (tau - 1) * residual))
        if loss > result.fun + 1e-08 * max(1, abs(result.fun)):
            return None
    out = np.full(len(y), np.nan)
    out[valid] = b - a @ beta
    return (out, beta)

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
    out = nan.copy()
    norm = v.div(v.mean())
    prev = lag(norm, session=variant == 'residual_corr')
    opening = (time <= 30).astype(float)
    closing = (time > 210).astype(float)
    for s in symbols:
        design = np.column_stack([np.ones(240), 10000 * ro[s], prev[s], opening, closing])
        fits = [quantile_fit(norm[s].to_numpy(), design, tau, 60, min_norm=variant == 'residual_corr') for tau in (0.8,)]
        if any((x is None for x in fits)):
            continue
        aa = fits[0][0]
        bb = ro[s].to_numpy()
        good = np.isfinite(aa) & np.isfinite(bb)
        if good.sum() >= 3 and np.std(aa[good]) > 0 and (np.std(bb[good]) > 0):
            out[s] = np.corrcoef(aa[good], bb[good])[0, 1]
    return {'d': out}

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
@fixed_factor('quantile_unexpected_high_volume_return_corr_21d', {})
class Factor_quantile_unexpected_high_volume_return_corr_21d(MinuteFactor):
    name = 'quantile_unexpected_high_volume_return_corr_21d'
    description = '在收益、时段和量能延续条件下提取高分位成交量残差，研究异常交易是否偏向价格上涨或承压时刻。 原文：[兴业证券最新研究！ 一个IC和分层超级炸裂的因子诞生了！](https://zhuanlan.zhihu.com/p/2097107862862436306)。'
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
