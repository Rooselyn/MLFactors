"""去季节性相关收益先行：ã_{d,m}=(a_{d,m}−mean_{d−20:d−1}a_m)/std_{d−20:d−1}a_m；corr(abs(l_{m−1}),ã_m)。

来源: [DolphinDB公式与源码](https://docs.dolphindb.cn/zh/tutorials/hf_to_lf_factor.html)
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
    'amount': ParquetInput("MLFactors/data/zz500/stock_minute/*/*.parquet", 'amount', date_column='trade_time'),
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



@register_factor
@fixed_factor('rpt_ddb_deseasonalized_pv_return_leads_20d', {})
class Factor_rpt_ddb_deseasonalized_pv_return_leads_20d(MinuteFactor):
    name = 'rpt_ddb_deseasonalized_pv_return_leads_20d'
    description = '去季节性相关收益先行'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 20

    def __init__(self):
        super().__init__(('close', 'amount'),minute_window_days=21)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        days=pd.DatetimeIndex(minute_data.attrs['trade_dates'])
        values=[day_panels(minute_data,d,universe,self.minute_fields,daily_data) for d in days]
        if len(values)!=21:return pd.Series(np.nan,index=symbols)
        array=np.stack([p['amount'].to_numpy() for p in values[:20]])
        base=pd.DataFrame(np.mean(array,axis=0),index=values[-1]['amount'].index,columns=universe)
        scale=pd.DataFrame(np.std(array,axis=0,ddof=1),index=base.index,columns=universe)
        a=(values[-1]['amount']-base)/scale.replace(0,np.nan)
        l=np.log(values[-1]['close']/lag(values[-1]['close'])).abs()
        value=corr(lag(l),a)
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
