"""随波逐流：h_d按高低额差；mean_{j≠i}abs(Spearman20(h_i,h_j))。

来源: [方正《个股成交额的市场跟随性与“水中行舟”》／实现](https://bigquant.com/data/datasources/hf_bar1m_c_fz_boat_in_water)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import MinuteFactor
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor


INPUTS = {
    'open_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'open_hfq'),
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
    'circ_mv': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'circ_mv'),
}
MINUTE_INPUTS = {
    'close': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'close', date_column='trade_time', adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'adj_factor')),
    'amount': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'amount', date_column='trade_time'),
}

def peer_mean(frame, minimum, absolute=False, spearman=False):
    corr = frame.rank().corr(min_periods=minimum) if spearman else frame.corr(min_periods=minimum)
    np.fill_diagonal(corr.values, np.nan)
    return (corr.abs() if absolute else corr).mean(axis=1)

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
    r=p['close']/lag(p['close'])-1
    market_std=r.std(axis=1)
    quiet=market_std<market_std.mean()
    lone=peer_mean(p['amount'].where(quiet,axis=0),30,absolute=True)
    lone=complete_day(lone,p)
    c=daily_panel(daily_data,'close_hfq');o=daily_panel(daily_data,'open_hfq')
    threshold=(c/o-1).rolling(20).mean().loc[day].reindex(r.columns)
    localret=p['close'].div(o.loc[day].reindex(r.columns),axis=1)-1
    high=p['amount'].where(localret.gt(threshold),0).sum(min_count=180)
    low=p['amount'].where(localret.lt(threshold),0).sum(min_count=180)
    spread=(high-low)/(current(daily_data,'circ_mv',day,r.columns)*10000)
    spread=complete_day(spread,p).where(threshold.notna())
    return {'lone':lone,'spread':spread}

@register_factor
@fixed_factor('rpt_fz_go_with_flow_20d', {})
class Factor_rpt_fz_go_with_flow_20d(MinuteFactor):
    name = 'rpt_fz_go_with_flow_20d'
    description = '随波逐流'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 38

    def __init__(self):
        super().__init__(('close', 'amount'),minute_window_days=20)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        flow=peer_mean(s['spread'].tail(20),20,absolute=True,spearman=True)
        value=flow
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
