"""全潮汐：NV_m=Σ_{j=m−4}^{m+4}v_j，p=argmax NV，a=argmin_{m<p}NV，b=argmin_{m>p}NV；S(s,e)=(c_e/c_s−1)/(e−s)；mean20(S(a,b))。

边界约定：峰位p仅在前后均存在有效NV观测的分钟中取最大值，并列取最早；即排除首末有效NV位置；这是防止无一侧谷值的本地边界补定，仍要求完整20个交易日。

来源: [方正《个股成交量的潮汐变化》／实现](https://bigquant.com/data/datasources/cn_stock_factors_hf_fz_tide)
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

def roll(x, n, operation='std', center=False):
    return pd.concat([getattr(part.rolling(n,min_periods=n,center=center),operation)()
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

def day_stats(p,daily_data,day):
    nv=roll(p['vol'],9,'sum',center=True)
    out={key:pd.Series(np.nan,index=p['vol'].columns) for key in ['full','strong','weak']}
    for symbol in p['vol']:
        if p['vol'][symbol].count()<180:continue
        n=nv[symbol].reset_index(drop=True); c=p['close'][symbol].reset_index(drop=True)
        valid_positions=n.index[n.notna()]
        if len(valid_positions)<3:continue
        # A peak must admit an observed trough on both sides. Exclude the
        # first/last valid neighbourhood, preserving earliest-time tie breaks.
        peak=n.loc[valid_positions[1:-1]].idxmax()
        before=n.iloc[:peak];after=n.iloc[peak+1:]
        if before.notna().sum()==0 or after.notna().sum()==0:continue
        a,b=before.idxmin(),after.idxmin()
        if not np.isfinite(c.loc[[a,peak,b]]).all():continue
        speed=lambda start,end:(c[end]/c[start]-1)/(end-start)
        out['full'][symbol]=speed(a,b)
        strong,weak=((a,peak),(peak,b)) if n[a]<n[b] else ((peak,b),(a,peak))
        out['strong'][symbol]=speed(*strong);out['weak'][symbol]=speed(*weak)
    return out

@register_factor
@fixed_factor('rpt_fz_full_tide_20d', {})
class Factor_rpt_fz_full_tide_20d(MinuteFactor):
    name = 'rpt_fz_full_tide_20d'
    description = '全潮汐'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 19

    def __init__(self):
        super().__init__(('close', 'vol'),minute_window_days=20)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        value=aggregate(s['full'],'mean')
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
