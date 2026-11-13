"""协同效应：[Z(协同成交量)+Z(协同价差)]/2。

来源: [方正《协同效应》公开实现](https://bigquant.com/data/datasources/hf_bar1m_c_fz_synergy_effect)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import MinuteFactor
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor


INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
}
MINUTE_INPUTS = {
    'open': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'open', date_column='trade_time', adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'adj_factor')),
    'high': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'high', date_column='trade_time', adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'adj_factor')),
    'low': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'low', date_column='trade_time', adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'adj_factor')),
    'close': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'close', date_column='trade_time', adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'adj_factor')),
    'vol': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'vol', date_column='trade_time'),
}

def zs(s, winsor=False):
    s=s.copy()
    if winsor: s=s.clip(s.quantile(.01),s.quantile(.99))
    scale=s.std(ddof=1)
    return (s-s.mean())/scale if scale>0 else s*np.nan

def grid(day):
    day=pd.Timestamp(day).normalize()
    return pd.date_range(day+pd.Timedelta('9h31min'),day+pd.Timedelta('11h30min'),freq='min').append(
        pd.date_range(day+pd.Timedelta('13h1min'),day+pd.Timedelta('15h'),freq='min'))

def lag(x, n=1):
    result=x.shift(n)
    result.iloc[:n]=np.nan
    result.iloc[120:120+n]=np.nan
    return result

def roll(x, n, operation='std', center=False):
    return pd.concat([getattr(part.rolling(n,min_periods=n,center=center),operation)()
                      for part in (x.iloc[:120],x.iloc[120:])])

def corr(x,y,minimum=180):
    valid=x.notna() & y.notna()
    return x.where(valid).corrwith(y.where(valid)).where(valid.sum()>=minimum).replace([np.inf,-np.inf],np.nan)

def aggregate(frame, operation='mean', n=20):
    frame=frame.tail(n)
    answer=getattr(frame,operation)(axis=0)
    return answer.where(frame.notna().sum()==n) if len(frame)==n else answer*np.nan

def composite(frame, sign=1, winsor=False):
    return (zs(aggregate(frame),winsor)+sign*zs(aggregate(frame,'std'),winsor))/2

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

def daily_panel(data,field):
    return data[field].unstack('symbol').sort_index()

def synergy_counts(codes):
    n=len(codes[0].columns)
    scores=np.zeros((n,n),dtype=np.int32)
    paired=np.full((n,n),240,dtype=np.int32)
    for frame in codes:
        array=frame.to_numpy()
        valid=np.isfinite(array).astype(np.int32)
        paired=np.minimum(paired,valid.T@valid)
        for state in [-1,0,1]:
            members=(array==state).astype(np.int32)
            scores+=members.T@members
    return scores,paired

def day_stats(p,daily_data,day):
    c=p['close'];v=p['vol'];r=c/lag(c)-1
    total=sum(roll(p[field],5,'sum') for field in ['open','high','low','close'])
    squared=sum(roll(p[field]**2,5,'sum') for field in ['open','high','low','close'])
    mu=total/20;sigma=np.sqrt(((squared-total**2/20)/19).clip(lower=0))
    state=pd.DataFrame(np.where(c>mu+sigma,1,np.where(c<mu-sigma,-1,0)),index=c.index,columns=c.columns).where(mu.notna()&c.notna())
    proportion=v.div(v.sum(min_count=180).replace(0,np.nan),axis=1)
    group=proportion*np.nan
    for k in [-1,0,1]:
        total_share=proportion.where(state==k).sum(axis=1,min_count=1)
        group=group.where(state!=k,pd.DataFrame(np.broadcast_to(total_share.to_numpy()[:,None],c.shape),index=c.index,columns=c.columns))
    volume=corr(proportion,group)
    previous=daily_panel(daily_data,'close_hfq').shift(1).loc[day].reindex(c.columns)
    fallback=np.sign(c-lag(roll(c,5,'mean')))
    fallback=fallback.mask(fallback==0,np.sign(c.sub(previous,axis=1)))
    codes=[]
    for raw in [r,r-lag(roll(r,5,'mean')),v-lag(roll(v,5,'mean'))]:
        sign=np.sign(raw);codes.append(sign.mask(sign==0,fallback).where(raw.notna()))
    spread=pd.Series(np.nan,index=c.columns)
    good=(r.count()>=180)&(v.count()>=180)
    members=sorted(good.index[good]);daily_r=daily_panel(daily_data,'close_hfq').pct_change(fill_method=None).loc[day]
    if len(members)>=31:
        score,paired=synergy_counts([code.loc[:,members] for code in codes])
        for symbol in members:
            position=members.index(symbol)
            candidates=[j for j,other in enumerate(members) if other!=symbol and paired[position,j]>=180]
            chosen=[members[j] for j in sorted(candidates,key=lambda j:(-score[position,j],members[j]))[:30]]
            if len(chosen)==30 and daily_r.reindex(chosen+[symbol]).notna().all():spread[symbol]=daily_r[symbol]-daily_r[chosen].mean()
    return {'volume':volume,'spread':spread}

@register_factor
@fixed_factor('rpt_fz_synergy_effect_20d', {})
class Factor_rpt_fz_synergy_effect_20d(MinuteFactor):
    name = 'rpt_fz_synergy_effect_20d'
    description = '协同效应'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 20

    def __init__(self):
        super().__init__(('open', 'high', 'low', 'close', 'vol'),minute_window_days=20)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        value=(zs(composite(s['volume']))+zs(composite(s['spread'])))/2
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
