"""价先量行：mean20[corr(c_{m−1},v_m)]；固定错位1个交易分钟，正名按先发生的序列定义。

来源: [原报全文](https://www.scribd.com/document/840833885/20210301-%E4%B8%9C%E5%90%B4%E8%AF%81%E5%88%B8-%E6%8A%80%E6%9C%AF%E5%88%86%E6%9E%90%E6%8B%A5%E6%8A%B1%E9%80%89%E8%82%A1%E5%9B%A0%E5%AD%90-%E7%B3%BB%E5%88%97%E7%A0%94%E7%A9%B6-%E4%BA%94-CPV%E5%9B%A0%E5%AD%90%E7%A7%BB%E4%BD%8D%E7%89%88-%E4%BB%B7%E9%87%8F%E8%87%AA%E7%9B%B8%E5%85%B3%E6%80%A7%E4%B8%AD%E8%95%B4%E8%97%8F%E7%9A%84%E9%80%89%E8%82%A1%E4%BF%A1%E6%81%AF)；[东吴《CPV因子抢跑版》PDF](https://bigdata-s3.wmcloud.com/researchreport/2021-05/5a3a96171b8fd33cb8c0733dccbe162e.pdf)；[券商研究结论HTML](https://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/lastest/rptid/674533858177/index.phtml)
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
    return {'rho':corr(lag(p['close']),p['vol'])}

@register_factor
@fixed_factor('rpt_dw_price_leads_volume_20d', {})
class Factor_rpt_dw_price_leads_volume_20d(MinuteFactor):
    name = 'rpt_dw_price_leads_volume_20d'
    description = '价先量行'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 19

    def __init__(self):
        super().__init__(('close', 'vol'),minute_window_days=20)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        value=aggregate(s['rho'])
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
