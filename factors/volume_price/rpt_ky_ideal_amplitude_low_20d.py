"""低价振幅：20日按C排序，各取最高/最低5日；mean_{低价5日}(H/L−1)。

来源: [开源《振幅因子的隐藏结构》／实现](https://bigquant.com/data/datasources/hf_prefactors_ky_ideal_amplitude)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
    'high_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'high_hfq'),
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'low_hfq'),
}

def rolling_select(key, value, window, count, mode):
    output = key * np.nan
    for col in key:
        a, b = key[col].to_numpy(), value[col].to_numpy()
        for i in range(window - 1, len(a)):
            kk, vv = a[i-window+1:i+1], b[i-window+1:i+1]
            if not (np.isfinite(kk).all() and np.isfinite(vv).all()):
                continue
            order = np.argsort(kk, kind='stable')
            if mode == 'sum_low': result = vv[order[:count]].sum()
            elif mode == 'high': result = vv[order[-count:]].mean()
            elif mode == 'low': result = vv[order[:count]].mean()
            else: result = vv[order[-count:]].mean() - vv[order[:count]].mean()
            output.loc[output.index[i], col] = result
    return output

@register_factor
@fixed_factor('rpt_ky_ideal_amplitude_low_20d', {})
class Factor_rpt_ky_ideal_amplitude_low_20d(BaseFactor):
    name = 'rpt_ky_ideal_amplitude_low_20d'
    description = '低价振幅'
    warmup_days = 19
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        value = rolling_select(x['close_hfq'],x['high_hfq']/x['low_hfq']-1,20,5,'low')
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
