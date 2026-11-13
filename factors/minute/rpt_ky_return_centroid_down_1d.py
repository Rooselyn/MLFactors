"""跌幅时间重心：U=Σ_{r>0}m r_m/Σ_{r>0}r_m，D=Σ_{r<0}m r_m/Σ_{r<0}r_m；输出Σ_{r<0}m r_m/Σ_{r<0}r_m。

来源: [开源《日内分钟收益率的时序特征》PDF](https://bigdata-s3.wmcloud.com/researchreport/2022-12/714f739f36237d630fe3a3bbaab4f803.pdf)；[公开实现](https://bigquant.com/data/datasources/cn_stock_factors_hf_ky_intraday_behavior)
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
    number=np.arange(1,241)
    up=r.where(r>0);down=r.where(r<0)
    u=(up.mul(number,axis=0).sum(min_count=1)/up.sum(min_count=1)).where(r.count()>=180)
    d=(down.mul(number,axis=0).sum(min_count=1)/down.sum(min_count=1)).where(r.count()>=180)
    return {'up':u,'down':d,'deviation':residual_series(d,[u])}

@register_factor
@fixed_factor('rpt_ky_return_centroid_down_1d', {})
class Factor_rpt_ky_return_centroid_down_1d(MinuteFactor):
    name = 'rpt_ky_return_centroid_down_1d'
    description = '跌幅时间重心'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 0

    def __init__(self):
        super().__init__(('close',),minute_window_days=1)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        s=collect(self,minute_data,daily_data,universe)
        value=s['down'].iloc[-1]
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
