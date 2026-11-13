"""标准化盈利惊喜8季度本地版（Seasonal EPS surprise）。
Δ_q=EPS_q−EPS_{q−4}；对前4个明确季度的同比差分取有效样本，至少3项；
SUE=(Δ_q−mean(Δ_{q−1:q−4}))/max(std(Δ_{q−1:q−4},ddof=1),0.01元/股)。
缺报告不补值，不把公告行当季度；0.01是观测尺度的固定正则下界。
来源: [EarningsSurprise／OSAP源码](https://github.com/OpenSourceAP/CrossSection/blob/master/Signals/LegacyStataCode/Predictors/EarningsSurprise.do)
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {'q_eps': ParquetInput('MLFactors/data/zz500/financial_indicator/*/*.parquet',
    'q_eps', date_column='ann_date', announcement_columns=('ann_date',), filters=())}
SPEC = {'name':'rpt_osap_eps_surprise_local_pit_8q', 'engine':'financial', 'annual':False,
        'leaves':{f'e{k}':['financial_indicator','q_eps','QY',k] for k in range(9)}}

def seasonal_surprise(env):
    current=env['e0']-env['e4']
    changes=np.stack([(env[f'e{k}']-env[f'e{k+4}']).to_numpy() for k in range(1,5)])
    valid=np.isfinite(changes)
    count=valid.sum(axis=0)
    mean=np.divide(np.where(valid,changes,0).sum(axis=0),count,
                   out=np.full(current.shape,np.nan),where=count>0)
    variance=np.divide(np.where(valid,(changes-mean)**2,0).sum(axis=0),count-1,
                       out=np.full(current.shape,np.nan),where=count>1)
    scale=np.maximum(np.sqrt(variance),.01)
    value=pd.DataFrame((current.to_numpy()-mean)/scale,index=current.index,columns=current.columns)
    return value.where(count>=3)

@register_factor
@fixed_factor('rpt_osap_eps_surprise_local_pit_8q', {})
class Factor_rpt_osap_eps_surprise_local_pit_8q(PublicFactor):
    name='rpt_osap_eps_surprise_local_pit_8q'
    description='标准化盈利惊喜8季度本地版（Seasonal EPS surprise）'
    INPUTS=INPUTS
    SPEC=SPEC
    warmup_days=100000

    def generate_signals(self,data,constituents=None):
        dates=pd.DatetimeIndex(data.index.get_level_values('date').unique()).sort_values()
        symbols=data.index.get_level_values('symbol').unique().sort_values()
        reports=_formula_calculations.read_reports(self.INPUTS,end=dates.max(),symbols=list(symbols))
        env,self.available_ann_dates=_formula_calculations.leaf_panels(self.SPEC,reports,dates,symbols,return_available=True)
        value=seasonal_surprise(env)
        return value.replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
