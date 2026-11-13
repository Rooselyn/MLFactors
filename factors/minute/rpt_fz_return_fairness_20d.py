"""收益公平：正v按当日极大似然λ做Box–Cox后差分；以差分均值±std分E+/E−；V±=mean_{E±}std(r_m,…,r_{m+4})，R±=mean_{E±}r_m；mean20[u×abs(R+−R−)]。

来源: [方正《成交量激增与骤降时刻的对称性》／实现](https://bigquant.com/data/datasources/hf_bar1m_c_fz_equal_treatment)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import MinuteFactor
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

from scipy import stats as scipy_stats

INPUTS = {
    'open_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'open_hfq'),
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
}
MINUTE_INPUTS = {
    'close': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'close', date_column='trade_time', adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'adj_factor')),
    'vol': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'vol', date_column='trade_time'),
}

def grid(day):
    day=pd.Timestamp(day).normalize()
    return pd.date_range(day+pd.Timedelta('9h31min'),day+pd.Timedelta('11h30min'),freq='min').append(
        pd.date_range(day+pd.Timedelta('13h1min'),day+pd.Timedelta('15h'),freq='min'))

def lag(x, n=1):
    result=x.shift(n)
    result.iloc[:n]=np.nan
    result.iloc[120:120+n]=np.nan
    return result

def forward_std(x, n=5):
    return pd.concat([part.iloc[::-1].rolling(n,min_periods=n).std().iloc[::-1]
                      for part in (x.iloc[:120],x.iloc[120:])])

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

def current(data,field,day,columns):
    return daily_panel(data,field).reindex(index=[day],columns=columns).iloc[0]

def complete_day(value, p, minimum=180):
    valid=pd.DataFrame(True,index=next(iter(p.values())).index,columns=value.index)
    for frame in p.values():valid &= frame.notna()
    return value.where(valid.sum()>=minimum)

def day_stats(p,daily_data,day):
    v=p['vol'];transformed=v*np.nan
    for symbol in v:
        good=v[symbol]>0;values=v.loc[good,symbol]
        if len(values)<180 or values.nunique()<2:continue
        try:transformed.loc[good,symbol]=scipy_stats.boxcox(values.to_numpy())[0]
        except (ValueError,FloatingPointError):continue
    delta=transformed-lag(transformed)
    up=delta.gt(delta.mean()+delta.std());down=delta.lt(delta.mean()-delta.std())
    r=p['close']/lag(p['close'])-1;fv=forward_std(r)
    u=current(daily_data,'close_hfq',day,r.columns)/current(daily_data,'open_hfq',day,r.columns)-1
    return {'ret':complete_day(u*(r.where(up).mean()-r.where(down).mean()).abs(),p),
            'vol':complete_day(u*(fv.where(up).mean()-fv.where(down).mean()).abs(),p)}

@register_factor
@fixed_factor('rpt_fz_return_fairness_20d', {})
class Factor_rpt_fz_return_fairness_20d(MinuteFactor):
    name = 'rpt_fz_return_fairness_20d'
    description = '收益公平'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 19

    def __init__(self):
        super().__init__(('close', 'vol'),minute_window_days=20)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        value=aggregate(s['ret'])
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
