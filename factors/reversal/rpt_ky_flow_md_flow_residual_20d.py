"""md分档残差资金流：CIS_md=Σ20(B_md−S_md)/Σ20 abs(B_md−S_md)，Ret20=C/C_{−20}−1；输出Res(CIS_md∣Ret20)。

来源: [开源资金流研究／公开实现](https://bigquant.com/data/datasources/cn_stock_factors_hf_ky_moneyflow_strength)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'buy_md_amount': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'buy_md_amount'),
    'sell_md_amount': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'sell_md_amount'),
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
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
@fixed_factor('rpt_ky_flow_md_flow_residual_20d', {})
class Factor_rpt_ky_flow_md_flow_residual_20d(BaseFactor):
    name = 'rpt_ky_flow_md_flow_residual_20d'
    description = 'md分档残差资金流'
    warmup_days = 20
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        buy,sell = x['buy_md_amount']*10000,x['sell_md_amount']*10000
        net=buy-sell
        cis = net.rolling(20).sum()/net.abs().rolling(20).sum().replace(0,np.nan)
        ret = x['close_hfq']/x['close_hfq'].shift(20)-1
        value = res(cis,[ret],eligible)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
