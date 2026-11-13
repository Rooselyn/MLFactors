"""趋势资金相对均价申万版：E={m:v_{d,m}>Q90(v_{此前5日所有分钟})}，VW_S=Σ_S(v_mc_m)/Σ_Sv_m；Res(mean20(VW_E/VW_全−1)∣ln总市值、申万一级哑变量)。

来源: [国盛原作者《基于趋势资金日内交易行为的选股因子》全文](https://finance.sina.com.cn/stock/stockzmt/2024-06-03/doc-inaxmham4932631.shtml)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import MinuteFactor
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor


INPUTS = {
    'total_mv': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'total_mv'),
    'industry_sw_1': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'industry_sw_1'),
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

def daily_panel(data,field):
    return data[field].unstack('symbol').sort_index()

def current(data,field,day,columns):
    return daily_panel(data,field).reindex(index=[day],columns=columns).iloc[0]

def industry_residual(value, cap, industry):
    labels=industry.astype('string')
    valid=np.isfinite(value)&np.isfinite(cap)&labels.notna()&labels.str.strip().ne('')
    # Build the design on actual regression observations. A category belonging
    # only to missing signals otherwise adds an all-zero column and rejects OLS.
    labels=labels.where(valid)
    dummies=pd.get_dummies(labels,dtype=float)
    regressors=[cap.where(valid)]+[dummies[col].where(valid) for col in dummies.columns[1:]]
    return residual_series(value.where(valid),regressors)



@register_factor
@fixed_factor('rpt_gs_trend_relative_price_local_20d', {})
class Factor_rpt_gs_trend_relative_price_local_20d(MinuteFactor):
    name = 'rpt_gs_trend_relative_price_local_20d'
    description = '趋势资金相对均价申万版'
    INPUTS = INPUTS
    MINUTE_INPUTS = MINUTE_INPUTS
    warmup_days = 24

    def __init__(self):
        super().__init__(('close', 'vol'),minute_window_days=25)
        self._day_cache = {}

    def calculate_daily_factor(self, trade_date, symbols, daily_data, minute_data):
        if len(symbols)==0:
            return pd.Series(index=symbols,dtype=float,name=self.name)
        universe=sorted(set(minute_data.index.get_level_values('symbol')) | set(symbols))
        days=pd.DatetimeIndex(minute_data.attrs['trade_dates'])
        ps=[day_panels(minute_data,d,universe,self.minute_fields,daily_data) for d in days]
        net=[];relative=[];outdays=[]
        start=0 if 'all_local' in self.name else 5
        for i in range(start,len(days)):
            p=ps[i];v,c=p['vol'],p['close']
            valid=v.notna()&c.notna()
            if start:
                history=np.stack([ps[j]['vol'].to_numpy() for j in range(i-5,i)])
                threshold=pd.Series(np.nanquantile(history.reshape(-1,len(universe)),.9,axis=0),index=universe)
                enough=(np.isfinite(history).sum(axis=1)>=180).all(axis=0)
                threshold=threshold.where(enough)
                selected=v.gt(threshold)&valid
            else:selected=valid
            vs=v.where(selected);cs=c.where(selected)
            base=cs.mean()
            floatshares=current(daily_data,'float_share',days[i],universe)*10000 if 'float_share' in daily_data else pd.Series(np.nan,index=universe)
            n=(vs.where(cs.lt(base),0).where(selected).sum(min_count=1)-vs.where(cs.gt(base),0).where(selected).sum(min_count=1))/floatshares.replace(0,np.nan)
            n=n.where(selected.sum()>0).where(valid.sum()>=180)
            vw=(vs*cs).sum(min_count=1)/vs.sum(min_count=1).replace(0,np.nan)
            whole=(v*c).sum(min_count=180)/v.sum(min_count=180).replace(0,np.nan)
            net.append(n);relative.append(vw/whole-1);outdays.append(days[i])
        cap=np.log(current(daily_data,'total_mv',trade_date,universe)*10000)
        industry=current(daily_data,'industry_sw_1',trade_date,universe)
        n=industry_residual(aggregate(pd.DataFrame(net,index=outdays)),cap,industry)
        r=industry_residual(aggregate(pd.DataFrame(relative,index=outdays)),cap,industry)
        value=r
        return value.reindex(symbols).astype(float).replace([np.inf,-np.inf],np.nan).rename(self.name)
