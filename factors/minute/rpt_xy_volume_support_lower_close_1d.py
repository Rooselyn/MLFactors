"""支撑下沿差：按当日未复权分币收盘价合并分钟量，众量价p0；以abs(p−p0)升序纳入价格层，首次达到全天50%量得集合S，pL=minS,pU=maxS；输出pL−C。

来源: [兴业《成交量分布中的Alpha》及PDF入口](https://fudan.bigquant.com/wiki/doc/8bghnLBtpA)；[DolphinDB公式与源码](https://docs.dolphindb.cn/zh/tutorials/hf_to_lf_factor.html)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import MinuteFactor
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor


INPUTS = {
    'high': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'high'),
    'low': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'low'),
    'close': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close'),
}
MINUTE_INPUTS = {
    'close': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'close', date_column='trade_time'),
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

def daily_panel(data,field):
    return data[field].unstack('symbol').sort_index()

def current(data,field,day,columns):
    return daily_panel(data,field).reindex(index=[day],columns=columns).iloc[0]

def day_stats(p,daily_data,day):
    result={k:pd.Series(np.nan,index=p['close'].columns) for k in ['lower','upper']}
    for symbol in p['close']:
        c,v=p['close'][symbol],p['vol'][symbol]
        valid=c.notna()&v.notna()
        if valid.sum()<180:continue
        price=np.rint(c[valid]*100).astype(int)
        volume=v[valid].groupby(price).sum().sort_index()
        if volume.sum()<=0:continue
        mode=volume.idxmax()
        order=sorted(volume.index,key=lambda cent:(abs(cent-mode),cent))
        cumulative=0;chosen=[]
        for cent in order:
            chosen.append(cent);cumulative+=volume[cent]
            if cumulative>=volume.sum()*.5:break
        result['lower'][symbol]=min(chosen)/100;result['upper'][symbol]=max(chosen)/100
    return result

@register_factor
@fixed_factor('rpt_xy_volume_support_lower_close_1d', {})
class Factor_rpt_xy_volume_support_lower_close_1d(MinuteFactor):
    name = 'rpt_xy_volume_support_lower_close_1d'
    description = '支撑下沿差'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 0

    def __init__(self):
        super().__init__(('close', 'vol'),minute_window_days=1)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        value=s['lower'].iloc[-1]-current(daily_data,'close',trade_date,universe)
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
