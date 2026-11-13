"""资本利得突出量滚动移植：最近255日剔除最近5日，余下250日分成50个5交易日块；按由近到远k=1,…,50，e_k=t−5k，U_k=clip[Σ_{d=e_k−4}^{e_k}V_d/(total_share_{e_k}×10000),0,1]；w_k=U_kΠ_{j<k}(1−U_j)，R_t=Σw_kC_{e_k}/Σw_k；CGO_t=(C_{t−5}−R_t)/C_{t−5}。

来源: [Grinblatt–Han《Prospect Theory, Mental Accounting, and Momentum》PDF](https://depot.som.yale.edu/icf/papers/fileuploads/2533/original/00-71.pdf)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
    'vol': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'vol'),
    'total_share': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'total_share'),
}


@register_factor
@fixed_factor('rpt_gh_capital_gains_overhang_255N5d', {})
class Factor_rpt_gh_capital_gains_overhang_255N5d(BaseFactor):
    name = 'rpt_gh_capital_gains_overhang_255N5d'
    description = '一年滚动资本利得突出量本地版（Rolling capital gains overhang）'
    warmup_days = 255
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        c = x['close_hfq']; block_vol = (x['vol']*100).rolling(5).sum()
        u = (block_vol/(x['total_share']*10000)).clip(0,1)
        numerator, denominator, survive = c*0, c*0, c*0+1
        valid = c.notna()
        for k in range(1,51):
            uk, ck = u.shift(5*k), c.shift(5*k)
            valid &= uk.notna() & ck.notna()
            weight = uk*survive
            numerator += weight*ck
            denominator += weight
            survive *= 1-uk
        reference = numerator/denominator.replace(0,np.nan)
        value = ((c.shift(5)-reference)/c.shift(5)).where(valid)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
