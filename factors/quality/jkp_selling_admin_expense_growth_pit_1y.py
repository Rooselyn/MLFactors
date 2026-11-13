"""jkp_selling_admin_expense_growth_pit_1y。

X_y=Y(financial_income.sell_exp+financial_income.admin_exp); F=-(X_y/LagFY(X_y,1)-1)
观察经营组织与获客费用的扩张压力，不能单凭费用增长认定效率下降。 原文：[JKP公开研究因子定义：var_growth；selling_admin_expense](https://github.com/bkelly-lab/jkp-data/blob/main/src/jkp/data/aux_functions.py)。
Y=AnnualPIT，仅使用截至信号日已公告的同一完整财年；跨表取共同最新可用年，所有金额元，缺失科目不补0，缺年不跳期。来源按知乎“4_因子动物园与复制”指向的JKP官方仓库逐项核对；为中国财报字段映射版，不宣称全球源数据库逐值一致。相邻两个年报完整，基期X须正；只保留一年增长，不重复收录三年窗口。优先股的明确0基期不计算相对增速。带息债务用字典interestdebt，资本开支用购建长期资产支付现金，均明确为本地科目对应。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import ast
import numpy as np
import pandas as pd
from scipy.signal import lfilter
import operator
from functools import lru_cache
import re
from scipy import stats
import copy
from factors.base import _formula_calculations
from factors.base import eligibility
INPUTS = {'financial_income__admin_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'admin_exp', date_column='ann_date', expression='admin_exp', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)), 'financial_income__sell_exp': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'sell_exp', date_column='ann_date', expression='sell_exp', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),))}
FORMULA = 'X_y=Y(financial_income.sell_exp+financial_income.admin_exp); F=-(X_y/LagFY(X_y,1)-1)'
RECIPE = {'family': 'financial_expression', 'program': 'X_y=Y(financial_income.sell_exp+financial_income.admin_exp); F=-(X_y/Pos(LagFY(X_y,1))-1)'}

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

def finite(x):
    if isinstance(x, (pd.DataFrame, pd.Series)):
        return x.replace([np.inf, -np.inf], np.nan)
    return np.where(np.isfinite(x), x, np.nan) if np.ndim(x) else x if np.isfinite(x) else np.nan

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

class FinancialFormula(Formula):

    def call(self, name, args, kwargs):
        if name in ('FinancialMean', 'FinancialStd'):
            arrays = np.stack([a.to_numpy(float) if isinstance(a, pd.DataFrame) else np.full(args[0].shape, a) for a in args])
            v = arrays.mean(axis=0) if name == 'FinancialMean' else arrays.std(axis=0, ddof=int(kwargs.get('ddof', 1)))
            return pd.DataFrame(v, index=args[0].index, columns=args[0].columns)
        return super().call(name, args, kwargs)
SELECTORS = {'Y': 'Y', 'AnnualPIT': 'Y', 'PITAnnual': 'Y', 'Q': 'Q', 'PITQ': 'B', 'PIT': 'B', 'TTM_PIT': 'T'}

class FinancialProgram:
    """展开财报期运算后才投影到交易日，LagQ不会变成交易日shift。"""

    def __init__(self, program):
        self.leaves = {}
        self.locals = {}
        self.annual = False
        statements = []
        for stmt in ast.parse(program.replace('^', '**')).body:
            if not isinstance(stmt, ast.Assign):
                raise ValueError('财务配方须为显式赋值序列')
            self.locals[stmt.targets[0].id] = copy.deepcopy(stmt.value)
            value = self.expand(stmt.value)
            statements.append(ast.Assign(targets=stmt.targets, value=value))
        self.program = ast.unparse(ast.fix_missing_locations(ast.Module(body=statements, type_ignores=[])))

    def expand(self, node, lag=0, mode=None, seen=frozenset()):
        if isinstance(node, ast.Name) and node.id in self.locals and (node.id not in seen):
            return self.expand(self.locals[node.id], lag, mode, seen | {node.id})
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name in ('LagFY', 'LagQ', 'DeltaFY'):
                k = 1 if len(node.args) == 1 else ast.literal_eval(node.args[1])
                if name == 'DeltaFY':
                    return ast.BinOp(self.expand(node.args[0], lag, mode, seen), ast.Sub(), self.expand(node.args[0], lag + 4, mode, seen))
                return self.expand(node.args[0], lag + int(k) * (4 if name == 'LagFY' else 1), mode, seen)
            if name in SELECTORS:
                selected = SELECTORS[name]
                self.annual |= selected == 'Y'
                return self.expand(node.args[0], lag, selected, seen)
            if name in ('Mean', 'Std'):
                args = [self.expand(a, lag, mode, seen) for a in node.args]
                return ast.Call(ast.Name('Financial' + name, ast.Load()), args, node.keywords)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id.startswith('financial_'):
            if mode is None:
                raise ValueError(f'财务字段未指明时点模式: {ast.unparse(node)}')
            leaf = (node.value.id, node.attr, mode, lag)
            key = 'fin_' + str(list(self.leaves.values()).index(leaf)) if leaf in self.leaves.values() else 'fin_' + str(len(self.leaves))
            self.leaves[key] = leaf
            return ast.Name(key, ast.Load())
        result = copy.copy(node)
        for (field, value) in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                setattr(result, field, self.expand(value, lag, mode, seen))
            elif isinstance(value, list):
                setattr(result, field, [self.expand(v, lag, mode, seen) if isinstance(v, ast.AST) else v for v in value])
        return result

class FinancialContext:

    def __init__(self, inputs, dates, symbols, reports=None):
        self.inputs = inputs
        self.dates = dates
        self.symbols = symbols
        self.reports = reports if reports is not None else _formula_calculations.read_reports({k: v for (k, v) in inputs.items() if 'financial_' in v.path}, end=dates.max(), symbols=list(symbols))

    def panels(self, leaves, annual=False):
        return _formula_calculations.leaf_panels({'leaves': leaves, 'annual': annual}, self.reports, self.dates, self.symbols, return_available=True)

    def program(self, program, values, eligible):
        compiled = FinancialProgram(program)
        (env, available) = self.panels(compiled.leaves, compiled.annual)
        self.available = available
        return FinancialFormula({**values, **env}, eligible).run(compiled.program)

def compute_financial(recipe, context, values, eligible):
    family = recipe['family']
    variant = recipe.get('variant', '')
    value = context.program(recipe['program'], values, eligible)
    return value

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

@register_factor
@fixed_factor('jkp_selling_admin_expense_growth_pit_1y', {})
class Factor_jkp_selling_admin_expense_growth_pit_1y(BaseFactor):
    name = 'jkp_selling_admin_expense_growth_pit_1y'
    description = '观察经营组织与获客费用的扩张压力，不能单凭费用增长认定效率下降。 原文：[JKP公开研究因子定义：var_growth；selling_admin_expense](https://github.com/bkelly-lab/jkp-data/blob/main/src/jkp/data/aux_functions.py)。'
    INPUTS = INPUTS
    FORMULA = FORMULA
    RECIPE = RECIPE
    warmup_days = 100000
    PRESERVE_REPORT_HISTORY = True

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        (v, dates, symbols) = daily_values(data, self.INPUTS)
        if data.empty:
            return pd.DataFrame(index=dates, columns=symbols, dtype=float)
        e = eligibility(data, dates, symbols)
        recipe = self.RECIPE
        with np.errstate(all='ignore'):
            context = FinancialContext(self.INPUTS, dates, symbols)
            value = compute_financial(recipe, context, v, e)
            if hasattr(context, 'available'):
                self.available_ann_dates = context.available
        return finite(value).astype(float).where(e).rename_axis(index='date', columns='symbol')
