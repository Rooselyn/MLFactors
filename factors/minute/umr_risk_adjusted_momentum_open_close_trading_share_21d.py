"""umr_risk_adjusted_momentum_open_close_trading_share_21d。

r=close_hfq/L1(close_hfq)-1; M=Sum_cs(total_mv*r with vol>0)/Sum_cs(total_mv with vol>0); e=r-M; r5_k=Last_k(stock_minute.close)/Last_(k-1)(stock_minute.close)-1,k=2..48 of 5-minute bars; A_openclose=Sum(stock_minute.amount at first 30 and last 30 trading minutes); Q=A_openclose/(10000*circ_mv); F=M21((M21(Q)-Q)*e)
将早尾盘成交金额相对流通市值相对自身常态的下降与股票超额收益相乘后平滑，研究风险改善背景下的价格延续；与单独风险指标或普通收益动量不同。 原文：[UMR因子，风险和超额收益相乘之后，反转变动量！](https://zhuanlan.zhihu.com/p/2027864361603999153)。
按作者同时点总市值权重构造项目股票市场收益，正市值且vol>0才参与，至少100股；当日停牌/无成交股票缺失，不把无法交易的0收益作为风险改善。风险与最终均值均21日、各至少17有效值。五分钟数据由现有分钟表按上午/下午各24根聚合，不跨午休合并K线；相邻五分钟收盘收益按日内顺序，早尾盘各6根=各30分钟。金额元、circ_mv万元故乘10000；不收缺少真实主动买单、单笔交易笔数所需的另外三个风险版本。相对TR统一后复权价，修正源码跨复权口径比较风险。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from collections import OrderedDict
import numpy as np
import pandas as pd
from factors.base import eligibility
from factors.base import MinuteFactor
import ast
from scipy.signal import lfilter
import operator
from functools import lru_cache
import re
from scipy import stats
import warnings
from factors.inputs import read_inputs
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'vol': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'vol'), 'circ_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'circ_mv')}
MINUTE_INPUTS = {'close': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'close', date_column='trade_time'), 'amount': ParquetInput('MLFactors/data/zz500/stock_minute/*/*.parquet', 'amount', date_column='trade_time')}
FORMULA = 'r=close_hfq/L1(close_hfq)-1; M=Sum_cs(total_mv*r with vol>0)/Sum_cs(total_mv with vol>0); e=r-M; r5_k=Last_k(stock_minute.close)/Last_(k-1)(stock_minute.close)-1,k=2..48 of 5-minute bars; A_openclose=Sum(stock_minute.amount at first 30 and last 30 trading minutes); Q=A_openclose/(10000*circ_mv); F=M21((M21(Q)-Q)*e)'
RECIPE = {'family': 'umr', 'variant': 'openclose', 'window': 21, 'min_days': 17}

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

    def scalar(self, name, k):
        if name not in self._scalar_cache:
            self._scalar_cache[name] = self.v[name].reindex(index=self.days, columns=self.symbols)
        return self._scalar_cache[name].iloc[k]

def choose(condition, yes, no):
    if isinstance(condition, (pd.DataFrame, pd.Series)):
        a = yes if isinstance(yes, type(condition)) else condition * 0 + yes
        b = no if isinstance(no, type(condition)) else condition * 0 + no
        return a.where(condition.eq(1), b).where(condition.notna())
    return np.where(pd.notna(condition), np.where(condition == 1, yes, no), np.nan)

def compare(a, b, op):
    valid = pd.notna(a) & pd.notna(b)
    value = op(a, b)
    if isinstance(value, (pd.DataFrame, pd.Series)):
        return value.astype(float).where(valid)
    return np.where(valid, value.astype(float) if hasattr(value, 'astype') else float(value), np.nan)

def cs_residual(y, *xs, intercept=True, minimum=None, return_fitted=False):
    out = y * np.nan
    for i in range(len(y)):
        target = y.iloc[i].to_numpy(float)
        xx = np.column_stack([x.iloc[i].to_numpy(float) for x in xs])
        valid = np.isfinite(target) & np.isfinite(xx).all(axis=1)
        if valid.sum() < (minimum or xx.shape[1] + int(intercept)):
            continue
        design = xx[valid]
        if intercept and design.shape[1] == 1 and (np.ptp(design[:, 0]) == 0):
            fitted = np.full(valid.sum(), target[valid].mean())
        else:
            if intercept:
                design = np.column_stack([np.ones(valid.sum()), design])
            if np.linalg.matrix_rank(design) < design.shape[1]:
                continue
            fitted = design @ np.linalg.lstsq(design, target[valid], rcond=None)[0]
        out.iloc[i, np.flatnonzero(valid)] = fitted if return_fitted else target[valid] - fitted
    return out

def div(a, b):
    if isinstance(b, (pd.DataFrame, pd.Series)):
        b = b.where(np.isfinite(b) & b.ne(0))
    elif np.ndim(b):
        b = np.where(np.isfinite(b) & (b != 0), b, np.nan)
    elif not np.isfinite(b) or b == 0:
        b = np.nan
    with np.errstate(all='ignore'):
        return finite(a / b)

def finite_ema(x, n, seed_length=500):
    alpha = 2 / (n + 1)
    if seed_length == 1:
        return x.copy()
    decay = 1 - alpha
    array = x.to_numpy(float)
    known = np.isfinite(array)
    filtered = lfilter([alpha], [1.0, -decay], np.where(known, array, 0.0), axis=0)
    value = filtered.copy()
    tail = decay ** seed_length
    if len(value) > seed_length:
        value[seed_length:] -= tail * filtered[:-seed_length]
    if len(value) >= seed_length:
        value[seed_length - 1:] += tail * np.where(known, array, 0.0)[:len(value) - seed_length + 1]
    count = np.cumsum(known, axis=0, dtype=np.int64)
    if len(count) > seed_length:
        count[seed_length:] -= count[:-seed_length].copy()
    value[count < seed_length] = np.nan
    return pd.DataFrame(value, index=x.index, columns=x.columns)

def group_transform(x, groups, method='mean', ddof=0):
    out = x * np.nan
    for d in x.index:
        g = groups.loc[d]
        valid = g.notna() & g.ne('')
        (xx, gg) = (x.loc[d, valid], g[valid])
        if method == 'rank':
            rr = xx.groupby(gg).rank(method='average')
            nn = xx.groupby(gg).transform('count')
            y = (rr - 1) / (nn - 1).replace(0, np.nan)
            y = y.mask(xx.notna() & nn.eq(1), 0.5)
        elif method == 'z':
            y = (xx - xx.groupby(gg).transform('mean')) / xx.groupby(gg).transform('std', ddof=ddof).replace(0, np.nan)
        else:
            y = xx.groupby(gg).transform(method, **{'ddof': ddof} if method == 'std' else {})
        out.loc[d, valid] = y
    return out

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

def pair_rolling(a, b, n, method='corr', ddof=0):
    valid = np.isfinite(a) & np.isfinite(b)
    (aa, bb) = (a.where(valid), b.where(valid))
    if method == 'corr':
        result = aa.rolling(int(n), min_periods=int(n)).corr(bb)
        return result.where(rolling(aa, n, 'var') > 0).where(rolling(bb, n, 'var') > 0)
    return aa.rolling(int(n), min_periods=int(n)).cov(bb, ddof=ddof)

@lru_cache(maxsize=4096)
def parse_program(program):
    tree = ast.parse(program.replace('^', '**'), mode='exec')
    allowed = (ast.Module, ast.Assign, ast.Expr, ast.Name, ast.Load, ast.Store, ast.Attribute, ast.Constant, ast.Call, ast.keyword, ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.Compare, ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.NotEq, ast.BoolOp, ast.And, ast.Or, ast.Not)
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(f'公式不支持语法: {type(node).__name__}')
        if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name)):
            raise ValueError('公式只能调用命名的白名单算子')
        if isinstance(node, ast.Assign) and (len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name)):
            raise ValueError('公式赋值左侧必须为一个局部变量')
    return tree

def rank(x, mode='unit', minimum=1, eligible=None):
    x = finite(x)
    if eligible is not None:
        x = x.where(eligible)
    count = x.count(axis=1)
    r = x.rank(axis=1, method='average')
    if mode == 'unit':
        out = div(r.sub(1), count.sub(1).replace(0, np.nan).to_numpy()[:, None])
        out = out.mask(x.notna() & count.eq(1).to_numpy()[:, None], 0.5)
    else:
        out = r.div(count.replace(0, np.nan), axis=0)
    return out.where(count.ge(minimum), axis=0)

def time_rank(x, n, mode='unit'):
    r = x.rolling(int(n), min_periods=int(n)).rank(method='average', pct=False)
    if mode == 'raw':
        return r
    if mode == 'pct':
        return r / n
    return (r - 1) / (n - 1) if n > 1 else r * 0 + 0.5

def trend(x, n, kind='slope', tiny=0):
    n = int(n)
    t = np.arange(1, n + 1, dtype=float)
    tc = t - t.mean()
    den = tc @ tc
    if den == 0:
        return x * np.nan
    mean = rolling(x, n)
    slope = x.rolling(n, min_periods=n).apply(lambda a: a @ tc / den, raw=True)
    if kind == 'slope':
        return slope
    if kind == 'resi':
        return x - mean - slope * tc[-1]
    return div(slope.pow(2) * den, rolling(x, n, 'var') * n).where(rolling(x, n, 'std') > tiny)

def weighted(x, weights):
    w = np.asarray(weights, float)
    w = w / w.sum()
    return x.rolling(len(w), min_periods=len(w)).apply(lambda a: a @ w, raw=True)

def zscore(x, ddof=0, eligible=None):
    if eligible is not None:
        x = x.where(eligible)
    return x.sub(x.mean(axis=1), axis=0).div(x.std(axis=1, ddof=ddof).replace(0, np.nan), axis=0)

class Formula:

    def __init__(self, values, eligible=None):
        self.values = dict(values)
        self.eligible = eligible

    def call(self, name, args, kwargs):
        x = args[0] if args else None
        if name == 'div':
            return div(*args)
        if name == 'Pos':
            return x.where(x > 0)
        if name in ('ln', 'log'):
            return log(x)
        if name == 'log10':
            return log(x, 10)
        if name == 'log2':
            return log(x, 2)
        if name == 'sqrt':
            return np.sqrt(x.where(x >= 0) if hasattr(x, 'where') else np.where(x >= 0, x, np.nan))
        if name == 'exp':
            return finite(np.exp(x))
        if name == 'abs':
            return abs(x)
        if name == 'sign':
            return np.sign(x)
        if name == 'tanh':
            return np.tanh(x)
        if name == 'floor':
            return np.floor(x)
        if name == 'clip':
            return x.clip(*args[1:])
        if name == 'Phi':
            return pd.DataFrame(stats.norm.cdf(x), index=x.index, columns=x.columns)
        if name == 'I':
            return x.astype(float)
        if name == 'IF':
            return choose(*args)
        if name in ('MAX', 'Max', 'max'):
            return self.reduce(args, np.maximum)
        if name in ('MIN', 'Min', 'min'):
            return self.reduce(args, np.minimum)
        if name in ('R', 'Rank', 'MLR'):
            return rank(x, eligible=self.eligible)
        if name == 'CSZ':
            return zscore(x, eligible=self.eligible)
        if name == 'CSRes':
            return cs_residual(*(a.where(self.eligible) if self.eligible is not None else a for a in args))
        if name in ('CSMean', 'CSMedian', 'CSMin', 'CSMax', 'CSStd', 'CSVar'):
            a = x.where(self.eligible) if self.eligible is not None else x
            method = {'CSMean': 'mean', 'CSMedian': 'median', 'CSMin': 'min', 'CSMax': 'max', 'CSStd': 'std', 'CSVar': 'var'}[name]
            k = {'ddof': kwargs.get('ddof', 0)} if method in ('std', 'var') else {}
            return a * 0 + getattr(a, method)(axis=1, **k).to_numpy()[:, None]
        if name in ('GZ', 'GRank'):
            return group_transform(x.where(self.eligible) if self.eligible is not None else x, args[1], 'z' if name == 'GZ' else 'rank')
        if name == 'P':
            return x.rolling(int(args[1]), min_periods=int(args[1])).quantile(args[2] / 100)
        if name in ('TopSum', 'TopMean', 'SDTop'):
            (n, k) = map(int, args[1:])
            method = {'TopSum': 'sum', 'TopMean': 'mean', 'SDTop': 'std'}[name]
            return x.rolling(n, min_periods=n).apply(lambda a: getattr(np.sort(a)[-k:], method)(), raw=True)
        if name == 'SignLog':
            return np.sign(x) * log(1 + abs(x))
        m = re.fullmatch('(L|M|S|Sum|SD|Std|Var|Max|Min|Mean|TRaw|TR|TSRank|MLT|Corr|Cov|W|Kurt|EMA|Quantile)(\\d+)', name)
        if m:
            (op, n) = (m.group(1), int(m.group(2)))
            if op == 'L':
                return x.shift(n)
            if op in ('TR', 'TSRank', 'MLT', 'TRaw'):
                return time_rank(x, n, 'raw' if op == 'TRaw' else 'pct' if op == 'MLT' else 'unit')
            if op in ('Corr', 'Cov'):
                return pair_rolling(x, args[1], n, op.lower())
            if op == 'W':
                return weighted(x, np.arange(1, n + 1))
            if op == 'EMA':
                return x.ewm(span=n, adjust=False, min_periods=1).mean().where(x.notna())
            if op == 'Quantile':
                return x.rolling(n, min_periods=n).quantile(args[1])
            method = {'M': 'mean', 'Mean': 'mean', 'S': 'sum', 'Sum': 'sum', 'SD': 'std', 'Std': 'std', 'Var': 'var', 'Max': 'max', 'Min': 'min', 'Kurt': 'kurt'}[op]
            return rolling(x, n, method, kwargs.get('ddof', 1 if op == 'Std' else 0))
        if name.startswith(('AB_', 'EV_', 'FM_')):
            return self.dialect(name, args, kwargs)
        raise ValueError(f'未实现的公式算子: {name}')

    @staticmethod
    def reduce(args, op):
        out = args[0]
        for a in args[1:]:
            out = op(out, a)
        return out

    def dialect(self, name, a, kw):
        (source, op) = name.split('_', 1)
        x = a[0]
        simple = {'Add': operator.add, 'Sub': operator.sub, 'Mul': operator.mul, 'Div': div, 'Neg': operator.neg, 'Abs': abs, 'Sign': np.sign, 'Power': np.power, 'POW': np.power, 'SignedPower': lambda x, p: np.sign(x) * abs(x) ** p, 'Greater': np.maximum, 'Less': np.minimum, 'Max2': np.maximum, 'Min2': np.minimum, 'MAX': np.maximum, 'MIN': np.minimum, 'EXP': np.exp, 'ABS': abs, 'SIGN': np.sign}
        if source == 'FM' and op in ('Greater', 'Less', 'Eq'):
            return compare(*a, {'Greater': operator.gt, 'Less': operator.lt, 'Eq': operator.eq}[op])
        if op in simple:
            return finite(simple[op](*a))
        if op in ('If', 'IfElse'):
            return choose(*a)
        if op in ('Gt', 'Lt', 'Ge', 'Le', 'Eq', 'Ne'):
            return compare(*a, {'Gt': operator.gt, 'Lt': operator.lt, 'Ge': operator.ge, 'Le': operator.le, 'Eq': operator.eq, 'Ne': operator.ne}[op])
        if op in ('And', 'Or'):
            return compare(a[0], a[1], lambda v, w: (v == 1) & (w == 1) if op == 'And' else (v == 1) | (w == 1))
        if op in ('Log', 'LOG'):
            return log(x, offset=1 if source == 'EV' else 0)
        if op in ('Sqrt', 'SQRT'):
            return np.sqrt(x.where(x >= 0))
        if op in ('Reciprocal', 'INV'):
            return div(1, x)
        if op == 'Clip':
            return x.clip(a[1], a[2])
        if op in ('RANK', 'CsRank'):
            return rank(x, 'pct', minimum=100 if source == 'FM' else 1, eligible=self.eligible)
        if op == 'ZSCORE':
            return zscore(x, ddof=1, eligible=self.eligible)
        if op == 'SEQUENCE':
            return ('sequence', int(x))
        if op in ('Ref', 'Delay', 'DELAY'):
            return x.shift(int(a[1]))
        if op in ('Delta', 'DELTA'):
            return x - x.shift(int(a[1]))
        if op == 'TS_PCTCHANGE':
            return div(x, x.shift(int(a[1]))) - 1
        if op in ('EMA', 'MACD', 'RSI'):

            def ema(v, n):
                return v.ewm(alpha=n if n < 1 else 2 / (n + 1), adjust=True, min_periods=1).mean().where(v.notna())
            if op == 'MACD':
                return ema(x, a[1]) - ema(x, a[2])
            if op == 'RSI':
                d = x.diff()
                u = ema(d.clip(lower=0), a[1])
                v = ema((-d).clip(lower=0), a[1])
                return 100 * div(u, u + v)
            return finite_ema(x, a[1]) if source == 'FM' else ema(x, a[1])
        if op in ('Corr', 'Cov', 'TS_CORR', 'TS_COVARIANCE'):
            return pair_rolling(x, a[1], int(a[2]), 'corr' if op in ('Corr', 'TS_CORR') else 'cov', ddof=0 if source == 'FM' else 1)
        if op in ('REGBETA', 'REGRESI'):
            (xx, n) = (a[1], int(a[2]))
            if isinstance(xx, tuple) and xx[0] == 'sequence':
                return trend(x, n, 'slope' if op == 'REGBETA' else 'resi')
            beta = div(pair_rolling(x, xx, n, 'cov', ddof=1), rolling(xx, n, 'var', ddof=1))
            return beta if op == 'REGBETA' else x - rolling(x, n) - beta * (xx - rolling(xx, n))
        if op == 'ATR':
            (high, low, close, n) = a
            previous = close.shift(1)
            tr = np.maximum(np.maximum(high - low, abs(high - previous)), abs(low - previous))
            return rolling(tr, int(n))
        if op in ('Slope', 'SLOPE', 'Rsquare', 'Resi'):
            return trend(x, int(a[1]), {'Slope': 'slope', 'SLOPE': 'slope', 'Rsquare': 'r2', 'Resi': 'resi'}[op], 2e-05 if source == 'AB' and op == 'Rsquare' else 0)
        n = int(a[1])
        if op in ('Rank', 'TsRank', 'TS_RANK'):
            return time_rank(x, n, 'pct')
        if op in ('WMA', 'DECAYLINEAR'):
            w = 0.9 ** np.arange(n - 1, -1, -1) if source == 'EV' and op == 'WMA' else np.arange(1, n + 1)
            return weighted(x, w) / (n if source == 'AB' and op == 'WMA' else 1)
        if op in ('Quantile', 'TS_QUANTILE'):
            return x.rolling(n, min_periods=n).quantile(a[2])
        if op in ('Mad', 'TS_MAD'):
            if source == 'EV':
                return rolling(abs(x - rolling(x, n, 'median')), n, 'median')
            fn = lambda v: np.mean(abs(v - v.mean()))
            return x.rolling(n, min_periods=n).apply(fn, raw=True)
        if op == 'TS_ZSCORE':
            return div(x - rolling(x, n), rolling(x, n, 'std', 1))
        if op in ('IdxMax', 'IdxMin', 'TS_ARGMAX', 'TS_ARGMIN', 'HIGHDAY', 'LOWDAY'):
            maximum = op in ('IdxMax', 'TS_ARGMAX', 'HIGHDAY')
            fn = np.argmax if maximum else np.argmin
            return x.rolling(n, min_periods=n).apply(lambda v: fn(v) + 1 if source == 'AB' else n - 1 - fn(v) + (1 if op in ('HIGHDAY', 'LOWDAY') else 0), raw=True)
        if op in ('BB_MIDDLE', 'BB_UPPER', 'BB_LOWER'):
            m = rolling(x, n)
            s = rolling(x, n, 'std', 1)
            return m if op == 'BB_MIDDLE' else m + s if op == 'BB_UPPER' else m - s
        if op in ('Skew', 'Kurt') and source == 'FM':
            k = 3 if op == 'Skew' else 4
            return x.rolling(n, min_periods=n).apply(lambda v: np.mean((v - v.mean()) ** k) / v.std() ** k if v.std() > 0 else np.nan, raw=True)
        methods = {'Mean': 'mean', 'SMA': 'mean', 'Sum': 'sum', 'Max': 'max', 'TsMax': 'max', 'Min': 'min', 'TsMin': 'min', 'Std': 'std', 'Var': 'var', 'Med': 'median', 'Skew': 'skew', 'Kurt': 'kurt', 'TS_MEAN': 'mean', 'TS_SUM': 'sum', 'TS_MAX': 'max', 'TS_MIN': 'min', 'TS_STD': 'std', 'TS_VAR': 'var', 'TS_SKEW': 'skew', 'COUNT': 'sum'}
        if op not in methods:
            raise ValueError(f'未实现的来源算子: {name}')
        return rolling(x, n, methods[op], 0 if source == 'FM' else 1)

    def node(self, n):
        if isinstance(n, ast.Name):
            return self.values[n.id]
        if isinstance(n, ast.Attribute):
            return self.values[ast.unparse(n)]
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.BinOp):
            (a, b) = (self.node(n.left), self.node(n.right))
            fn = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: div, ast.Pow: np.power}[type(n.op)]
            with np.errstate(all='ignore'):
                return finite(fn(a, b))
        if isinstance(n, ast.UnaryOp):
            a = self.node(n.operand)
            return -a if isinstance(n.op, ast.USub) else compare(a, 0, operator.eq) if isinstance(n.op, ast.Not) else a
        if isinstance(n, ast.Compare):
            if len(n.ops) != 1:
                raise ValueError('比较必须显式拆分')
            op = {ast.Gt: operator.gt, ast.Lt: operator.lt, ast.GtE: operator.ge, ast.LtE: operator.le, ast.Eq: operator.eq, ast.NotEq: operator.ne}[type(n.ops[0])]
            return compare(self.node(n.left), self.node(n.comparators[0]), op)
        if isinstance(n, ast.BoolOp):
            vals = [self.node(a) for a in n.values]
            result = vals[0]
            for v in vals[1:]:
                result = self.call('FM_And' if isinstance(n.op, ast.And) else 'FM_Or', [result, v], {})
            return result
        if isinstance(n, ast.Call):
            return self.call(n.func.id, [self.node(a) for a in n.args], {a.arg: self.node(a.value) for a in n.keywords})
        raise ValueError(f'未实现公式节点: {ast.dump(n)}')

    def run(self, program, result='F'):
        for statement in parse_program(program).body:
            if not isinstance(statement, ast.Assign):
                raise ValueError('公式必须由赋值语句构成')
            self.values[statement.targets[0].id] = self.node(statement.value)
        return finite(self.values[result])

def conditional_mean(x, condition, n):
    valid = x.notna() & condition.notna()
    return x.where(condition.eq(1)).rolling(n, min_periods=1).mean().where(valid.rolling(n, min_periods=n).sum().eq(n))

def winsor(x, q=0.01, mad=None):
    if mad is None:
        return x.clip(x.quantile(q, axis=1), x.quantile(1 - q, axis=1), axis=0)
    m = x.median(axis=1)
    s = x.sub(m, axis=0).abs().median(axis=1) * mad
    clipped = x.clip(m - s, m + s, axis=0)
    return clipped.where(s.ne(0), x, axis=0)

class ResearchFormula(Formula):

    def call(self, name, args, kwargs):
        if name == 'Scale':
            return div(args[0], abs(args[0]).where(self.eligible).sum(axis=1, min_count=1).to_numpy()[:, None])
        if name == 'WeightedMarket':
            (r, mv, vol) = args
            good = self.eligible & r.notna() & mv.gt(0) & vol.gt(0)
            value = div((r * mv).where(good).sum(axis=1, min_count=1), mv.where(good).sum(axis=1, min_count=1))
            value = value.where(good.sum(axis=1) >= 100)
            return (r * 0 + value.to_numpy()[:, None]).where(good)
        if name == 'MinimumMean':
            (x, n, minimum) = args
            value = x.rolling(n, min_periods=minimum).mean()
            value.iloc[:n - 1] = np.nan
            return value
        if name == 'TopStd':
            (x, n, k) = args
            return x.rolling(n, min_periods=n).apply(lambda a: np.sort(a)[-k:].std(ddof=1), raw=True)
        if name == 'MLR':
            return rank(args[0], 'pct', eligible=self.eligible)
        if re.fullmatch('MLT\\d+', name):
            n = int(name[3:])
            return args[0].rolling(n, min_periods=n).apply(lambda a: np.mean(a <= a[-1]), raw=True)
        if name == 'ML_E':
            (x, alpha) = args

            def calc(v):
                out = np.full(len(v), np.nan)
                state = 0.0
                count = 0
                for (i, a) in enumerate(v):
                    if np.isfinite(a):
                        state = alpha * a + (1 - alpha) * state
                        count += 1
                        out[i] = state
                return out
            self._ml_warmup = getattr(self, '_ml_warmup', []) + [x.notna().cumsum().ge(500)]
            return pd.DataFrame({s: calc(x[s].to_numpy(float)) for s in x}, index=x.index)
        if name == 'CondMean':
            return conditional_mean(*args)
        if name == 'Winsor':
            return winsor(args[0], args[1])
        if name == 'WinsorMAD':
            return winsor(args[0], mad=args[1])
        if name == 'EWM':
            return args[0].ewm(alpha=args[1], adjust=False, min_periods=1).mean().where(args[0].notna())
        if name == 'CentralMoment':
            (x, n, k) = args
            return x.rolling(n, min_periods=n).apply(lambda v: np.mean((v - v.mean()) ** k), raw=True)
        if name == 'TopSkew':
            (x, n, k, side) = args
            return x.rolling(n, min_periods=n).apply(lambda a: stats.skew(np.sort(a)[-k:] if side > 0 else np.sort(a)[:k], bias=False) if np.ptp(np.sort(a)[-k:] if side > 0 else np.sort(a)[:k]) > 0 else np.nan, raw=True)
        if name == 'SampleVol':
            return rolling(args[0], args[1], 'std', 1)
        if name == 'SampleMean':
            return rolling(*args)
        if name == 'Pos':
            return args[0].where(args[0] > 0)
        return super().call(name, args, kwargs)

    def run(self, program, result='F'):
        value = super().run(program, result)
        for mask in getattr(self, '_ml_warmup', []):
            value = value.where(mask)
        return value

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
    cc = c.to_numpy().reshape(48, 5, len(symbols))[:, -1, :]
    rr = cc[1:] / cc[:-1] - 1
    value = div(a.iloc[np.r_[0:30, 210:240]].sum(min_count=60), 10000 * ctx.scalar('circ_mv', k))
    return {'d': value}

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
    v = ctx.v
    daily_r = div(v['close_hfq'], v['close_hfq'].shift(1)) - 1
    market = ResearchFormula(v, ctx.e).call('WeightedMarket', [daily_r, v['total_mv'], v['vol']], {})
    q = panel.reindex(v['close_hfq'].index)
    inner = q.rolling(21, min_periods=17).mean()
    inner.iloc[:20] = np.nan
    result = ((inner - q) * (daily_r - market)).rolling(21, min_periods=17).mean()
    result.iloc[:20] = np.nan
    return result.reindex(ctx.days)

@register_factor
@fixed_factor('umr_risk_adjusted_momentum_open_close_trading_share_21d', {})
class Factor_umr_risk_adjusted_momentum_open_close_trading_share_21d(MinuteFactor):
    name = 'umr_risk_adjusted_momentum_open_close_trading_share_21d'
    description = '将早尾盘成交金额相对流通市值相对自身常态的下降与股票超额收益相乘后平滑，研究风险改善背景下的价格延续；与单独风险指标或普通收益动量不同。 原文：[UMR因子，风险和超额收益相乘之后，反转变动量！](https://zhuanlan.zhihu.com/p/2027864361603999153)。'
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
