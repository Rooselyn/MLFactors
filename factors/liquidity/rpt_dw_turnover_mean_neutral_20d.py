"""市值中性换手率：Res(mean20(T)∣ln浮动市值)。

来源: [东吴《量稳换手率》与附录PDF](https://file.iyanbao.com/pdf/61c3a-dd732cd7-7eb5-41d3-8c36-790eaa68132c.pdf)
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
@fixed_factor('rpt_dw_turnover_mean_neutral_20d', {})
class Factor_rpt_dw_turnover_mean_neutral_20d(BaseFactor):
    name = 'rpt_dw_turnover_mean_neutral_20d'
    description = '市值中性换手率'
    warmup_days = 19
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        t=x['turnover_rate']/100
        value = res(t.rolling(20).mean(),[np.log(x['circ_mv']*10000)],eligible)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
