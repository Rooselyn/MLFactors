"""significant_information_idiovol_turnover_60d。

r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; e=OLSResidual(r~1+FFLocalMKT+FFLocalSMB+FFLocalHML,last60days); S=Top20Days(stock_day.turnover_rate,last60days); D=sqrt(Mean(e_s^2,s in S)); F=D
用高换手日筛选信息显著样本，观察剔除市场、规模和价值共同变化后的特有风险。 原文：[显著信息特质波动率，花里胡哨的操作带来的提升肉眼不可见，最后还得靠黑科技！](https://zhuanlan.zhihu.com/p/2048154692660761543)。
采用公开代码对同一60日完整窗口回归后取残差，按选择变量最大的20日取均方根，不对20条再去均值。60日收益、控制组合及排序量均完整，矩阵满秩、残差非退化；并列按交易日期取较近者。FFLocal三控制组合按报告公共定义从本项目行情构造、无风险基准固定0，不调用缺失的官方风格收益字段。分钟波动日需至少200条当根开收盘有效收益。"""
from __future__ import annotations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import BaseFactor
import numpy as np
import pandas as pd
from factors.base import eligibility
INPUTS = {'close_hfq': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'close_hfq'), 'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'), 'pb': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'pb'), 'turnover_rate': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'turnover_rate')}
FORMULA = 'r=stock_day.close_hfq/L1(stock_day.close_hfq)-1; e=OLSResidual(r~1+FFLocalMKT+FFLocalSMB+FFLocalHML,last60days); S=Top20Days(stock_day.turnover_rate,last60days); D=sqrt(Mean(e_s^2,s in S)); F=D'
RECIPE = {'family': 'specific_information', 'variant': 'turnover'}

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
    score = v['turnover_rate']
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
@fixed_factor('significant_information_idiovol_turnover_60d', {})
class Factor_significant_information_idiovol_turnover_60d(BaseFactor):
    name = 'significant_information_idiovol_turnover_60d'
    description = '用高换手日筛选信息显著样本，观察剔除市场、规模和价值共同变化后的特有风险。 原文：[显著信息特质波动率，花里胡哨的操作带来的提升肉眼不可见，最后还得靠黑科技！](https://zhuanlan.zhihu.com/p/2048154692660761543)。'
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
