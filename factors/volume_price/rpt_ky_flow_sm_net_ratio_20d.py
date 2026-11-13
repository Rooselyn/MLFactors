"""sm分档净流入率S2：Σ20(B_sm−S_sm)/Σ20(B_sm+S_sm)；B/S=对应分档buy/sell金额×10000元，A=amount×1000元。

来源: [开源资金流研究／公开实现](https://bigquant.com/data/datasources/cn_stock_factors_hf_ky_moneyflow_strength)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'buy_sm_amount': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'buy_sm_amount'),
    'sell_sm_amount': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'sell_sm_amount'),
}


@register_factor
@fixed_factor('rpt_ky_flow_sm_net_ratio_20d', {})
class Factor_rpt_ky_flow_sm_net_ratio_20d(BaseFactor):
    name = 'rpt_ky_flow_sm_net_ratio_20d'
    description = 'sm分档净流入率S2'
    warmup_days = 20
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        buy,sell = x['buy_sm_amount']*10000,x['sell_sm_amount']*10000
        net=buy-sell
        value = net.rolling(20).sum()/((buy+sell).rolling(20).sum()).replace(0,np.nan)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
