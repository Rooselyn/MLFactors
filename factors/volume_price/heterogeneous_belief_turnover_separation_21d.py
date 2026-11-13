"""heterogeneous_belief_turnover_separation_21d。

r=close_hfq/L1(close_hfq)-1; z=(ln(total_mv),1/pe,pb/pe,close_hfq/L21(close_hfq)-1); E=M21(turnover_rate-CSMean(turnover_rate)); in last 21d: a_j=sqrt(Mean(z_j^2)); x_j=z_j/a_j; beta=RidgeOLS(r~1+x,penalty=n*1e-8 on slopes only); q_j=sign(beta_j)*z_j/a_j; gamma=RidgeOLS(turnover_rate~1+q,penalty=n*1e-8 on slopes only); D=gamma0+Sum(gamma_j*q_j,current t); F=turnover_rate-E-D
从换手率中剥离相对市场的流动性需求常态以及规模、估值、盈利和动量可解释交易，研究剩余异质信念交易；两阶段截距作用分别处理。 原文：[从42分钟到25秒：Codex把两次滚动回归提速约100倍 ！](https://zhuanlan.zhihu.com/p/2092725080396657377)。
依据配套计算说明：变量按窗口均方根而非中心化标准差缩放，第一阶段只用斜率确定方向，截距不传作贡献；第二阶段含截距且其截距计入D。数值稳定阈值补为1e-12，近零尺度置1、近零beta对应贡献列置0；窗口至少15共同有效日，当日全部输入有效，21日窗口形成前不输出，E至少17/21值。源码岭惩罚未明定补为1e-8，明确为稳定化本地版本；不把近乎等价的trading_hb_2再计为新因子。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'pe': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pe'), 'pb': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pb'), 'turnover_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate')}
FORMULA = 'r=close_hfq/L1(close_hfq)-1; z=(ln(total_mv),1/pe,pb/pe,close_hfq/L21(close_hfq)-1); E=M21(turnover_rate-CSMean(turnover_rate)); in last 21d: a_j=sqrt(Mean(z_j^2)); x_j=z_j/a_j; beta=RidgeOLS(r~1+x,penalty=n*1e-8 on slopes only); q_j=sign(beta_j)*z_j/a_j; gamma=RidgeOLS(turnover_rate~1+q,penalty=n*1e-8 on slopes only); D=gamma0+Sum(gamma_j*q_j,current t); F=turnover_rate-E-D'
RECIPE = {'family': 'hb_turnover'}

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

def log(x, base=np.e, offset=0):
    z = x + offset
    if isinstance(z, (pd.DataFrame, pd.Series)):
        z = z.where(z > 0)
    else:
        z = np.where(z > 0, z, np.nan)
    return np.log(z) / np.log(base)

def compute_daily(recipe, v, e):
    family = recipe['family']
    variant = recipe.get('variant', '')
    c = v.get('close_hfq', v.get('close'))
    r = div(c, c.shift(1)) - 1 if c is not None else None
    t = v['turnover_rate']
    xs = [log(v['total_mv']), div(1, v['pe']), div(v['pb'], v['pe']), div(c, c.shift(21)) - 1]
    out = t * np.nan
    for j in range(c.shape[1]):
        for i in range(20, len(c)):
            a = np.column_stack([x.iloc[i - 20:i + 1, j] for x in xs])
            y = r.iloc[i - 20:i + 1, j].to_numpy()
            target = t.iloc[i - 20:i + 1, j].to_numpy()
            good = np.isfinite(a).all(axis=1) & np.isfinite(y) & np.isfinite(target)
            if good.sum() < 15 or not good[-1]:
                continue
            (a, y, target) = (a[good], y[good], target[good])
            scale = np.sqrt(np.mean(a * a, axis=0))
            scale[scale < 1e-12] = 1
            a = a / scale

            def fit(xx, yy):
                z = np.column_stack([np.ones(len(xx)), xx])
                pen = np.diag([0] + [len(xx) * 1e-08] * xx.shape[1])
                return np.linalg.solve(z.T @ z + pen, z.T @ yy)
            b = fit(a, y)[1:]
            sg = np.sign(b)
            sg[abs(b) < 1e-12] = 0
            q = a * sg
            gamma = fit(q, target)
            out.iat[i, j] = gamma[0] + q[-1] @ gamma[1:]
    ex = (t - t.where(e).mean(axis=1).to_numpy()[:, None]).rolling(21, min_periods=17).mean()
    ex.iloc[:20] = np.nan
    return t - ex - out

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
@fixed_factor('heterogeneous_belief_turnover_separation_21d', {})
class Factor_heterogeneous_belief_turnover_separation_21d(BaseFactor):
    name = 'heterogeneous_belief_turnover_separation_21d'
    description = '从换手率中剥离相对市场的流动性需求常态以及规模、估值、盈利和动量可解释交易，研究剩余异质信念交易；两阶段截距作用分别处理。 原文：[从42分钟到25秒：Codex把两次滚动回归提速约100倍 ！](https://zhuanlan.zhihu.com/p/2092725080396657377)。'
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
            value = compute_daily(recipe, v, e)
        return finite(value).astype(float).where(e).rename_axis(index='date', columns='symbol')
