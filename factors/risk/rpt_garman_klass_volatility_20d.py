"""Garman–Klass波动率：sqrt[(252/20)Σ{0.5ln²(H/L)−(2ln2−1)ln²(C/O)}]。

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
@fixed_factor('rpt_garman_klass_volatility_20d', {})
class Factor_rpt_garman_klass_volatility_20d(BaseFactor):
    name = 'rpt_garman_klass_volatility_20d'
    description = 'Garman–Klass波动率'
    warmup_days = 20
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        daily=.5*np.log(x['high_hfq']/x['low_hfq']).pow(2)-(2*np.log(2)-1)*np.log(x['close_hfq']/x['open_hfq']).pow(2)
        variance=252*daily.rolling(20).mean()
        value=np.sqrt(variance.where(variance>=0))
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
