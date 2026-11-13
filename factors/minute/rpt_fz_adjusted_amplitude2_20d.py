"""修正振幅2：B=H/L−1；K=2(H/L_{−1}−1−ln(H/L_{−1}))−ln²(H/L_{−1})；J为日Taylor跳跃度；mean20[F(K_d−mean_csK_d)×B]。

来源: [公开实现](https://bigquant.com/data/datasources/hf_bar1m_c_fz_moth_to_flame)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import MinuteFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor


INPUTS = {
    'high_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'high_hfq'),
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'low_hfq'),
}
MINUTE_INPUTS = {
    'close': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'close', date_column='trade_time', adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'adj_factor')),
}

def flip(x, eligible):
    difference = x.sub(x.where(eligible).mean(axis=1), axis=0)
    return np.sign(difference).replace(0, 1).where(difference.notna())

def grid(day):
    day=pd.Timestamp(day).normalize()
    return pd.date_range(day+pd.Timedelta('9h31min'),day+pd.Timedelta('11h30min'),freq='min').append(
        pd.date_range(day+pd.Timedelta('13h1min'),day+pd.Timedelta('15h'),freq='min'))

def lag(x, n=1):
    result=x.shift(n)
    result.iloc[:n]=np.nan
    result.iloc[120:120+n]=np.nan
    return result

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

def daily_panel(data,field):
    return data[field].unstack('symbol').sort_index()

def day_stats(p,daily_data,day):
    l=np.log(p['close']/lag(p['close']))
    value=(2*(np.expm1(l)-l)-l*l).mean().where(l.count()>=180)
    return {'jump':value}

@register_factor
@fixed_factor('rpt_fz_adjusted_amplitude2_20d', {})
class Factor_rpt_fz_adjusted_amplitude2_20d(MinuteFactor):
    name = 'rpt_fz_adjusted_amplitude2_20d'
    description = '修正振幅2'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 20

    def __init__(self):
        super().__init__(('close',),minute_window_days=20)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        days=s['jump'].index
        h=daily_panel(daily_data,'high_hfq').reindex(columns=universe)
        l=daily_panel(daily_data,'low_hfq').reindex(columns=universe)
        b=(h/l-1).reindex(days)
        x=h/l.shift(1)
        k=(2*(x-1-np.log(x))-np.log(x)**2).reindex(days)
        e=eligibility(daily_data,*panels(daily_data,[])[1:]).reindex(index=days,columns=universe,fill_value=False)
        b1=aggregate(flip(s['jump'],e)*b)
        b2=aggregate(flip(k,e)*b)
        value=b2
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
