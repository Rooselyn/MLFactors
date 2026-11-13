"""耀眼波动率日值：E={m:Δv_m>mean_mΔv+std_mΔv}；D=mean_E(std(r_m,…,r_{m+4}))；x_d=abs(D−mean_csD)；输出x_d。

来源: [方正《成交量激增时刻蕴含的alpha信息》／实现](https://bigquant.com/data/datasources/cn_stock_factors_hf_fz_moderate_risk)
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

def lag(x, n=1):
    result=x.shift(n)
    result.iloc[:n]=np.nan
    result.iloc[120:120+n]=np.nan
    return result

def forward_std(x, n=5):
    return pd.concat([part.iloc[::-1].rolling(n,min_periods=n).std().iloc[::-1]
                      for part in (x.iloc[:120],x.iloc[120:])])

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
    r=p['close']/lag(p['close'])-1
    dv=p['vol']-lag(p['vol'])
    event=dv.gt(dv.mean()+dv.std())
    ret=r.where(event).mean()
    vol=forward_std(r).where(event).mean()
    ret=(ret-ret.mean()).abs().where(r.count()>=180)
    vol=(vol-vol.mean()).abs().where(r.count()>=180)
    return {'ret':ret,'vol':vol}

@register_factor
@fixed_factor('rpt_fz_dazzling_volatility_daily_1d', {})
class Factor_rpt_fz_dazzling_volatility_daily_1d(MinuteFactor):
    name = 'rpt_fz_dazzling_volatility_daily_1d'
    description = '耀眼波动率日值'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 0

    def __init__(self):
        super().__init__(('close', 'vol'),minute_window_days=1)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s = collect(self,minute_data,daily_data,universe)
        value = s['vol'].iloc[-1]
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
