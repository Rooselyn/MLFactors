"""换手率变异系数滚动移植：std126(T)/mean126(T)，T=turnover_rate/100；窗口截至信号日且包含当日。

来源: [中国A股特征库原始定义表](https://github.com/Quantactix/ChinaAShareEquityCharacteristics/blob/master/char_list.csv)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'turnover_rate': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'turnover_rate'),
}


@register_factor
@fixed_factor('rpt_ashare_turnover_cv_126d', {})
class Factor_rpt_ashare_turnover_cv_126d(BaseFactor):
    name = 'rpt_ashare_turnover_cv_126d'
    description = '换手率变异系数滚动移植'
    warmup_days = 126
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        t=x['turnover_rate']/100
        value = t.rolling(126).std()/t.rolling(126).mean().where(lambda v:v>0)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
