"""量岭间隔偏度：按同一钟点此前20日量均值μ与标准差σ，E=1(v>μ+σ)；P_m=E_m(1−E_{m−1})(1−E_{m+1})，R=E−P，G=1−E；合并最近20日各日内相邻R分钟间隔Δm；输出skew(Δm)。

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

def classified_history(minute_data,daily_data,universe,fields):
    days=pd.DatetimeIndex(minute_data.attrs['trade_dates'])
    ps=[day_panels(minute_data,d,universe,fields,daily_data) for d in days]
    output=[]
    for i in range(20,len(days)):
        p=ps[i]
        history=np.stack([ps[j]['vol'].to_numpy() for j in range(i-20,i)])
        mean=np.mean(history,axis=0);std=np.std(history,axis=0,ddof=1)
        baseline=pd.DataFrame(mean+std,index=p['vol'].index,columns=universe)
        valid=baseline.notna()&p['vol'].notna()
        e=p['vol'].gt(baseline).astype(float).where(valid)
        before=lag(e);after=e.shift(-1);after.iloc[[119,239]]=np.nan
        peak=(e*(1-before)*(1-after)).where(before.notna()&after.notna())
        ridge=e-peak;valley=(1-e).where(valid)
        output.append((days[i],p,e,peak,ridge,valley))
    return output



@register_factor
@fixed_factor('rpt_ky_ridge_interval_skew_20d', {})
class Factor_rpt_ky_ridge_interval_skew_20d(MinuteFactor):
    name = 'rpt_ky_ridge_interval_skew_20d'
    description = '量岭间隔偏度'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 39

    def __init__(self):
        super().__init__(('vol',),minute_window_days=40)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        history=classified_history(minute_data,daily_data,universe,self.minute_fields)
        if len(history)!=20:return pd.Series(np.nan,index=symbols)
        value=pd.Series(np.nan,index=universe)
        for symbol in universe:
            intervals=[]
            complete=True
            for day,p,e,peak,ridge,valley in history:
                if p['vol'][symbol].count()<180:complete=False;break
                state=ridge[symbol]
                for part in [state.iloc[:120],state.iloc[120:]]:
                    positions=np.flatnonzero(part.eq(1).to_numpy())
                    intervals.extend(np.diff(positions))
            series=pd.Series(intervals,dtype=float)
            if complete and len(series)>=4:value[symbol]=series.skew()
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
