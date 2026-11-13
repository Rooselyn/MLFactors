"""量稳换手变化：Res[std(T_{t−19:t})/std(T_{t−59:t−20})−1∣ln浮动市值]。

来源: [东吴《改进STR》附录PDF](https://file.iyanbao.com/pdf/61c3a-dd732cd7-7eb5-41d3-8c36-790eaa68132c.pdf#page=6)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'turnover_rate': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'turnover_rate'),
    'circ_mv': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'circ_mv'),
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

@register_factor
@fixed_factor('rpt_dw_turnover_stability_change_60d', {})
class Factor_rpt_dw_turnover_stability_change_60d(BaseFactor):
    name = 'rpt_dw_turnover_stability_change_60d'
    description = '量稳换手变化'
    warmup_days = 59
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        t=x['turnover_rate']/100
        value = res(t.rolling(20).std()/t.shift(20).rolling(40).std().replace(0,np.nan)-1,[np.log(x['circ_mv']*10000)],eligible)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
