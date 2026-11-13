"""价量相关性波动：ρ_d=corr_m(c_m,v_m)，A=Res(mean20ρ∣ln总市值)，B=Res(std20ρ∣ln总市值)；输出B。

来源: [东吴《高频价量相关性，意想不到的选股因子》／实现](https://bigquant.com/data/datasources/cn_stock_factors_hf_dw_cpv_uid_composite)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import MinuteFactor
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor


INPUTS = {
    'total_mv': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'total_mv'),
}
MINUTE_INPUTS = {
    'close': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'close', date_column='trade_time', adjustment=ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'adj_factor')),
    'vol': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'vol', date_column='trade_time'),
}

def res(y, regressors, eligible):
    result = y * np.nan
    for day in y.index:
        yy = y.loc[day].where(eligible.loc[day])
        xx = pd.concat([v.loc[day] for v in regressors], axis=1)
        valid = yy.notna() & xx.notna().all(axis=1)
        design = np.column_stack([np.ones(valid.sum()), xx.loc[valid].to_numpy(dtype=float)])
        if valid.sum() < max(20, 2 * design.shape[1]) or np.linalg.matrix_rank(design) != design.shape[1]:
            continue
        target = yy.loc[valid].to_numpy(dtype=float)
        result.loc[day, valid] = target - design @ np.linalg.lstsq(design, target, rcond=None)[0]
    return result

def residual_series(y, xs):
    target=y.rename(None).to_frame().T
    return res(target,[a.rename(None).to_frame().T for a in xs],target.notna()).iloc[0]

def grid(day):
    day=pd.Timestamp(day).normalize()
    return pd.date_range(day+pd.Timedelta('9h31min'),day+pd.Timedelta('11h30min'),freq='min').append(
        pd.date_range(day+pd.Timedelta('13h1min'),day+pd.Timedelta('15h'),freq='min'))

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

def daily_panel(data,field):
    return data[field].unstack('symbol').sort_index()

def current(data,field,day,columns):
    return daily_panel(data,field).reindex(index=[day],columns=columns).iloc[0]

def day_stats(p,daily_data,day):
    return {'rho':corr(p['close'],p['vol'])}

@register_factor
@fixed_factor('rpt_dw_pv_corr_std_20d', {})
class Factor_rpt_dw_pv_corr_std_20d(MinuteFactor):
    name = 'rpt_dw_pv_corr_std_20d'
    description = '价量相关性波动'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 19

    def __init__(self):
        super().__init__(('close', 'vol'),minute_window_days=20)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        cap=np.log(current(daily_data,'total_mv',trade_date,universe)*10000)
        a=residual_series(aggregate(s['rho']),[cap])
        b=residual_series(aggregate(s['rho'],'std'),[cap])
        value=b
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
