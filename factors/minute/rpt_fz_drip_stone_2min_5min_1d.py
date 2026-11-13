"""滴水穿石频谱版：剔除开盘1分钟和收盘3分钟；成交量按 median±3IQR 截断，去均值乘 Hann 窗；P_f=abs(rFFT(v))²；因子=Σ_{周期2～5分钟}P_f/Σ_{f>0}P_f。

来源: [方正《个股日内成交量周期性节奏刻画》／实现](https://bigquant.com/data/datasources/hf_bar1m_fz_drip_stone)
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
    answer=pd.Series(np.nan,index=p['vol'].columns)
    frequency=np.fft.rfftfreq(236,d=1)
    selected=(frequency>=1/5)&(frequency<=1/2)
    for symbol in answer.index:
        v=p['vol'][symbol].iloc[1:-3]
        if len(v)!=236 or not v.notna().all():continue
        median=v.median();iqr=v.quantile(.75)-v.quantile(.25)
        a=v.clip(median-3*iqr,median+3*iqr).to_numpy();a=(a-a.mean())*np.hanning(236)
        power=np.abs(np.fft.rfft(a))**2;total=power[frequency>0].sum()
        if total>0:answer[symbol]=power[selected].sum()/total
    return {'value':answer}

@register_factor
@fixed_factor('rpt_fz_drip_stone_2min_5min_1d', {})
class Factor_rpt_fz_drip_stone_2min_5min_1d(MinuteFactor):
    name = 'rpt_fz_drip_stone_2min_5min_1d'
    description = '滴水穿石频谱版'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 0

    def __init__(self):
        super().__init__(('vol',),minute_window_days=1)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        value=s['value'].iloc[-1]
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
