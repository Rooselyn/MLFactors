"""Yang–Zhang波动率：令 o=ln(O/C_{−1})，c=ln(C/O)，RS=mean_20[ln(H/O)ln(H/C)+ln(L/O)ln(L/C)]；σ=sqrt{252[var20(o)+k var20(c)+(1−k)RS]}，k=0.34/[1.34+(20+1)/(20−1)]。

来源: [TTR作者维护的波动率公式与实现](https://github.com/joshuaulrich/TTR/blob/master/R/volatility.R)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'open_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'open_hfq'),
    'high_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'high_hfq'),
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'low_hfq'),
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
}


@register_factor
@fixed_factor('rpt_yang_zhang_volatility_20d', {})
class Factor_rpt_yang_zhang_volatility_20d(BaseFactor):
    name = 'rpt_yang_zhang_volatility_20d'
    description = 'Yang–Zhang波动率'
    warmup_days = 20
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        o=np.log(x['open_hfq']/x['close_hfq'].shift(1));c=np.log(x['close_hfq']/x['open_hfq'])
        rs=np.log(x['high_hfq']/x['open_hfq'])*np.log(x['high_hfq']/x['close_hfq'])+np.log(x['low_hfq']/x['open_hfq'])*np.log(x['low_hfq']/x['close_hfq'])
        k=.34/(1.34+21/19)
        variance=252*(o.rolling(20).var()+k*c.rolling(20).var()+(1-k)*rs.rolling(20).mean())
        value=np.sqrt(variance.where(variance>=0))
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
