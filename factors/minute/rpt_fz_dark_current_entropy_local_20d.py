"""暗流涌动熵简化版：5分钟u_{i,k}=v_{i,k}/Σ_jv_{j,k}，p=u/Σ_ku；H_d=−Σp ln p；mean20(H)。

来源: [公开复现函数dark_current_entropy](https://github.com/Ryan8856/factor_research/blob/main/founder_factors/factors.py)；[平滑方式compute_factor](https://github.com/Ryan8856/factor_research/blob/main/founder_factors/common.py)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import MinuteFactor
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor


INPUTS = {}
MINUTE_INPUTS = {
    'vol': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'vol', date_column='trade_time'),
    'close': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'close', date_column='trade_time', adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'adj_factor')),
}

def grid(day):
    day=pd.Timestamp(day).normalize()
    return pd.date_range(day+pd.Timedelta('9h31min'),day+pd.Timedelta('11h30min'),freq='min').append(
        pd.date_range(day+pd.Timedelta('13h1min'),day+pd.Timedelta('15h'),freq='min'))

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

def buckets(p):
    out={}
    group=np.arange(240)//5
    for field,value in p.items():
        grouped=value.groupby(group)
        if field=='open':answer=grouped.first()
        elif field=='close':answer=grouped.last()
        elif field=='high':answer=grouped.max()
        elif field=='low':answer=grouped.min()
        else:answer=grouped.sum(min_count=5)
        out[field]=answer.where(grouped.count()==5)
    return out

def day_stats(p,daily_data,day):
    b=buckets(p);v=b['vol'];c=b['close']
    share=v.div(v.sum(axis=1,min_count=1).replace(0,np.nan),axis=0)
    prob=share.div(share.sum(min_count=24).replace(0,np.nan),axis=1)
    entropy=-(prob.where(prob>0)*np.log(prob.where(prob>0))).sum(min_count=24)
    prev=c.shift(1);prev.iloc[[0,24]]=np.nan
    impact=(c/prev-1).abs()/v.replace(0,np.nan)
    base=pd.concat([v.iloc[:24].shift(1).rolling(5).mean(),v.iloc[24:].shift(1).rolling(5).mean()])
    event=v>1.5*base
    valid=impact.notna()&base.notna()
    high=impact.where(event & valid);low=impact.where(~event & valid)
    ratio=(high.mean()/low.mean().replace(0,np.nan)).where((high.count()>=2)&(low.count()>=5))
    return {'entropy':entropy,'impact':ratio}

@register_factor
@fixed_factor('rpt_fz_dark_current_entropy_local_20d', {})
class Factor_rpt_fz_dark_current_entropy_local_20d(MinuteFactor):
    name = 'rpt_fz_dark_current_entropy_local_20d'
    description = '暗流涌动熵简化版'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 19

    def __init__(self):
        super().__init__(('vol', 'close'),minute_window_days=20)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        value=aggregate(s['entropy'])
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
