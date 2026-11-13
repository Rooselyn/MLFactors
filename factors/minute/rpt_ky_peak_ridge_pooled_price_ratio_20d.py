"""峰岭加权价格比：按同一钟点此前20日量均值μ与标准差σ，E=1(v>μ+σ)；P_m=E_m(1−E_{m−1})(1−E_{m+1})，R=E−P，G=1−E；P_S=Σ_Svc/Σ_Sv；P_{P,W}/P_{R,W}，P_{S,W}=Σ_{d∈W,m∈S}vc/Σ_{d∈W,m∈S}v。

来源: [开源《横看成岭侧成峰：日内成交量状态的划分与因子构建》原作者全文](https://finance.sina.com.cn/roll/2025-07-20/doc-infhcnsm4121126.shtml)
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

def classified_history(minute_data,daily_data,universe,fields,cache=None):
    days=pd.DatetimeIndex(minute_data.attrs['trade_dates'])
    cache={} if cache is None else cache
    identity=tuple(universe)
    panels=[]
    for day in days:
        key=('panel',pd.Timestamp(day),identity)
        if key not in cache:cache[key]=day_panels(minute_data,day,universe,fields,daily_data)
        panels.append(cache[key])
    output=[]
    for i in range(20,len(days)):
        key=('classification',pd.Timestamp(days[i]),identity)
        if key not in cache:
            p=panels[i]
            history=np.stack([panels[j]['vol'].to_numpy() for j in range(i-20,i)])
            baseline=pd.DataFrame(np.mean(history,axis=0)+np.std(history,axis=0,ddof=1),
                                  index=p['vol'].index,columns=universe)
            valid=baseline.notna()&p['vol'].notna()
            e=p['vol'].gt(baseline).astype(float).where(valid)
            before=lag(e);after=e.shift(-1);after.iloc[[119,239]]=np.nan
            peak=(e*(1-before)*(1-after)).where(before.notna()&after.notna())
            cache[key]=(days[i],p,e,peak,e-peak,(1-e).where(valid))
        output.append(cache[key])
    keep=set(days)
    for key in list(cache):
        if key[1] not in keep:del cache[key]
    return output



@register_factor
@fixed_factor('rpt_ky_peak_ridge_pooled_price_ratio_20d', {})
class Factor_rpt_ky_peak_ridge_pooled_price_ratio_20d(MinuteFactor):
    name = 'rpt_ky_peak_ridge_pooled_price_ratio_20d'
    description = '峰岭20日合并量加权价格比（Pooled peak-to-ridge price ratio）'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 39

    def __init__(self):
        super().__init__(('close', 'vol'),minute_window_days=40)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        if len(symbols)==0:return pd.Series(index=symbols,dtype=float,name=self.name)
        universe=sorted(set(minute_data.index.get_level_values('symbol').unique()) | set(symbols))
        history=classified_history(minute_data,daily_data,universe,self.minute_fields,self._day_cache)
        if len(history)!=20:return pd.Series(np.nan,index=symbols)

        groups=('peak','ridge')
        totals={group:np.zeros(len(universe)) for group in groups}
        quantities={group:np.zeros(len(universe)) for group in groups}
        complete=np.ones(len(universe),dtype=bool)
        for day,p,e,peak,ridge,valley in history:
            v=p['vol'].to_numpy();c=p['close'].to_numpy()
            states={'peak':peak.to_numpy(),'ridge':ridge.to_numpy(),'valley':valley.to_numpy(),'all':np.ones(v.shape)}
            valid=np.isfinite(v)&np.isfinite(c)&np.isfinite(e.to_numpy())&np.isfinite(states['peak'])&np.isfinite(states['ridge'])
            complete &= valid.sum(axis=0)>=180
            for group in groups:
                selected=valid&(states[group]==1)
                quantities[group]+=np.where(selected,v,0).sum(axis=0)
                totals[group]+=np.where(selected,v*c,0).sum(axis=0)
        prices={group:np.divide(totals[group],quantities[group],out=np.full(len(universe),np.nan),where=quantities[group]>0) for group in groups}
        result=np.divide(prices['peak'],prices['ridge'],out=np.full(len(universe),np.nan),where=prices['ridge']>0)
        value=pd.Series(result,index=universe).where(complete)
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
