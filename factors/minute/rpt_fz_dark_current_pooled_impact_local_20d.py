"""暗流涌动冲击简化版：5分钟I_k=abs(c_k/c_{k−1}−1)/v_k，E={k:v_k>1.5mean(v_{k−5:k−1})}；D_t=mean_{W_t,E}I/mean_{W_t,非E}I；W_t为最近20交易日，直接合并事件/对照观测，不取逐日比率均值。

来源: [公开复现函数dark_current_elasticity](https://github.com/Ryan8856/factor_research/blob/main/founder_factors/factors.py)；[平滑方式compute_factor](https://github.com/Ryan8856/factor_research/blob/main/founder_factors/common.py)
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

def grid(day):
    day=pd.Timestamp(day).normalize()
    return pd.date_range(day+pd.Timedelta('9h31min'),day+pd.Timedelta('11h30min'),freq='min').append(
        pd.date_range(day+pd.Timedelta('13h1min'),day+pd.Timedelta('15h'),freq='min'))

def day_panels(minute_data,day,symbols,fields,daily_data):
    index=grid(day)
    result={}
    day_data=minute_data.loc[(slice(index[0],index[-1]),slice(None)),list(fields)]
    for field in fields:
        value=day_data[field].unstack('symbol').reindex(index=index,columns=symbols).astype(float)
        value=value.where(np.isfinite(value)&(value.ge(0) if field in ['vol','amount'] else value.gt(0)))
        result[field]=value
    try:
        daily=daily_data.xs(day,level='date')
    except KeyError:
        daily=daily_data.iloc[:0].droplevel('date')
    eligible=daily['is_member'].reindex(symbols).astype('boolean').fillna(False).astype(bool)
    for state in ['is_st','is_suspended']:
        eligible &= ~daily[state].reindex(symbols).astype('boolean').fillna(True).astype(bool)
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
    b=buckets(p);v,c=b['vol'],b['close']
    previous=c.shift(1);previous.iloc[[0,24]]=np.nan
    impact=(c/previous-1).abs()/v.where(v>0)
    base=pd.concat([v.iloc[:24].shift(1).rolling(5).mean(),v.iloc[24:].shift(1).rolling(5).mean()])
    event=v>1.5*base
    valid=impact.notna()&base.notna()
    high=impact.where(event&valid);low=impact.where(~event&valid)
    complete=(p['close'].notna()&p['vol'].notna()).sum()>=180
    return {'high_sum':high.sum(min_count=1).where(high.count()>0,0),
            'high_n':high.count().astype(float),
            'low_sum':low.sum(min_count=1).where(low.count()>0,0),
            'low_n':low.count().astype(float),'complete':complete.astype(float)}

@register_factor
@fixed_factor('rpt_fz_dark_current_pooled_impact_local_20d', {})
class Factor_rpt_fz_dark_current_pooled_impact_local_20d(MinuteFactor):
    name = 'rpt_fz_dark_current_pooled_impact_local_20d'
    description = '暗流涌动20日合并冲击比本地版（Pooled impact ratio）'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 19

    def __init__(self):
        super().__init__(('close', 'vol'),minute_window_days=20)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        if len(symbols)==0:return pd.Series(index=symbols,dtype=float,name=self.name)
        universe=sorted(set(minute_data.index.get_level_values('symbol').unique()) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        complete=s['complete'].tail(20).sum().eq(20) if len(s['complete'])>=20 else pd.Series(False,index=universe)
        high_n=s['high_n'].tail(20).sum();low_n=s['low_n'].tail(20).sum()
        high=s['high_sum'].tail(20).sum()/high_n.where(high_n>0)
        low=s['low_sum'].tail(20).sum()/low_n.where(low_n>0)
        value=(high/low.where(low>0)).where(complete&(high_n>=40)&(low_n>=100))
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
