"""午蔽古木：同朝没晨雾日回归；mean20[F(Fstat−mean_csFstat)×abs(t(α))]。

来源: [公开实现](https://bigquant.com/data/datasources/hf_bar1m_c_fz_hidden_flower)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import MinuteFactor
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor


INPUTS = {}
MINUTE_INPUTS = {
    'close': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'close', date_column='trade_time', adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'adj_factor')),
    'vol': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'vol', date_column='trade_time'),
}

def flip(x, eligible):
    difference = x.sub(x.where(eligible).mean(axis=1), axis=0)
    return np.sign(difference).replace(0, 1).where(difference.notna())

def peer_mean(frame, minimum, absolute=False, spearman=False):
    corr = frame.rank().corr(min_periods=minimum) if spearman else frame.corr(min_periods=minimum)
    np.fill_diagonal(corr.values, np.nan)
    return (corr.abs() if absolute else corr).mean(axis=1)

def grid(day):
    day=pd.Timestamp(day).normalize()
    return pd.date_range(day+pd.Timedelta('9h31min'),day+pd.Timedelta('11h30min'),freq='min').append(
        pd.date_range(day+pd.Timedelta('13h1min'),day+pd.Timedelta('15h'),freq='min'))

def lag(x, n=1):
    result=x.shift(n)
    result.iloc[:n]=np.nan
    result.iloc[120:120+n]=np.nan
    return result

def corr(x,y,minimum=180):
    valid=x.notna() & y.notna()
    return x.where(valid).corrwith(y.where(valid)).where(valid.sum()>=minimum).replace([np.inf,-np.inf],np.nan)

def aggregate(frame, operation='mean', n=20):
    frame=frame.tail(n)
    answer=getattr(frame,operation)(axis=0)
    return answer.where(frame.notna().sum()==n) if len(frame)==n else answer*np.nan

def day_panels(minute_data,day,symbols,fields,daily_data):
    index=grid(day)
    result={}
    day_data=minute_data.loc[(slice(index[0],index[-1]),slice(None)),list(fields)]
    for field in fields:
        value=day_data[field].unstack('symbol').reindex(index=index,columns=symbols).astype(float)
        value=value.where(np.isfinite(value)&(value.ge(0) if field in ['vol','amount'] else value.gt(0)))
        result[field]=value
    eligible=daily_data['is_member'].unstack('symbol').reindex(index=[day],columns=symbols).fillna(False).iloc[0].astype(bool)
    for state in ['is_st','is_suspended']:
        eligible &= ~daily_data[state].unstack('symbol').reindex(index=[day],columns=symbols).fillna(True).iloc[0].astype(bool)
    valid=pd.DataFrame(True,index=index,columns=symbols)
    for value in result.values():valid &= value.notna()
    if {'high','low'}<=result.keys():
        valid &= result['high'].ge(result['low'])
        for field in ['open','close']:
            if field in result:valid &= result[field].ge(result['low']) & result[field].le(result['high'])
    valid.loc[:,~eligible]=False
    for field in result:result[field]=result[field].where(valid)
    return result

def collect(factor,minute_data,daily_data,symbols):
    days=pd.DatetimeIndex(minute_data.attrs.get('trade_dates',
                         minute_data.index.get_level_values('trade_time').normalize().unique())).sort_values()
    results=[]
    for day in days:
        key=(pd.Timestamp(day),tuple(symbols))
        if key not in factor._day_cache:
            panel=day_panels(minute_data,day,symbols,factor.minute_fields,daily_data)
            factor._day_cache[key]=day_stats(panel,daily_data,day)
        results.append(factor._day_cache[key])
    # Reuse day computations while bounding memory by the current lookback.
    factor._day_cache={key:value for key,value in factor._day_cache.items() if key[0] in days}
    names=set().union(*(r.keys() for r in results)) if results else set()
    return {name:pd.DataFrame([r[name] for r in results],index=days,columns=symbols) for name in names}

def day_stats(p,daily_data,day):
    r=p['close']/lag(p['close'])-1;dv=p['vol']-lag(p['vol'])
    lags=[lag(dv,k) if k else dv for k in range(6)]
    out={key:pd.Series(np.nan,index=r.columns) for key in ['mist','alpha_t','f']}
    for symbol in r:
        x=pd.concat([a[symbol] for a in lags],axis=1)
        ok=x.notna().all(axis=1)&r[symbol].notna()
        if ok.sum()<30:continue
        raw=x.loc[ok].to_numpy();scale=np.std(raw,axis=0)
        if (scale<=0).any():continue
        design=np.column_stack([np.ones(ok.sum()),raw/scale])
        target=r.loc[ok,symbol].to_numpy()
        if not np.isfinite(design).all() or not np.isfinite(target).all():continue
        # Solve OLS and its coefficient variances from the same SVD. Forming
        # X.T@X squares the condition number and can make a full-rank X singular.
        try:
            left,singular,right=np.linalg.svd(design,full_matrices=False)
        except np.linalg.LinAlgError:
            continue
        tolerance=singular[0]*max(design.shape)*np.finfo(float).eps
        if np.any(singular<=tolerance):continue
        inverse=right.T/singular
        beta=inverse@(left.T@target)
        errors=target-design@beta; rss=errors@errors; dof=len(target)-7
        if rss<=0:continue
        se=np.sqrt(np.sum(inverse**2,axis=1)*rss/dof)
        ts=beta/se
        out['mist'][symbol]=np.std(ts[2:7],ddof=1)
        out['alpha_t'][symbol]=ts[0]
        out['f'][symbol]=max(0,((np.sum((target-target.mean())**2)-rss)/6)/(rss/dof))
    return out

@register_factor
@fixed_factor('rpt_fz_ancient_tree_20d', {})
class Factor_rpt_fz_ancient_tree_20d(MinuteFactor):
    name = 'rpt_fz_ancient_tree_20d'
    description = '午蔽古木'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 19

    def __init__(self):
        super().__init__(('close', 'vol'),minute_window_days=20)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        mist=aggregate(s['mist'])
        e=s['f'].notna()
        ancient=aggregate(flip(s['f'],e)*s['alpha_t'].abs())
        frost=peer_mean(s['alpha_t'].tail(20),20,absolute=True)
        value=ancient
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
