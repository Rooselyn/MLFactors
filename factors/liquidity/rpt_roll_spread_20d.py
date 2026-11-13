"""Roll隐含价差：2sqrt(max(−cov20(ΔC_d,ΔC_{d−1}),0))；仅对已观测协方差作非负截断；输入缺失仍留NaN。

来源: [Roll原论文PDF](https://www.bauer.uh.edu/rsusmel/phd/roll1984.pdf)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
}


@register_factor
@fixed_factor('rpt_roll_spread_20d', {})
class Factor_rpt_roll_spread_20d(BaseFactor):
    name = 'rpt_roll_spread_20d'
    description = 'Roll价差非负截断本地版（Nonnegative Roll spread）'
    warmup_days = 21
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        delta=x['close_hfq'].diff()
        cov=delta.rolling(20).cov(delta.shift(1))
        value=2*np.sqrt((-cov).clip(lower=0))
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
