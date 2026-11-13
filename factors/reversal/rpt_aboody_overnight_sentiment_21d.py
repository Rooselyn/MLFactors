"""隔夜收益情绪滚动移植：mean21(g_d)，g_d=O_d/C_{d−1}−1；窗口包含信号日，要求21个有效隔夜收益。

来源: [Aboody等原论文PDF](https://anderson-review.ucla.edu/wp-content/uploads/2021/03/Aboody-et-al_overnight_returns_and_firmspecific_investor_sentiment_JFQA2018.pdf)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'open_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'open_hfq'),
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
}


@register_factor
@fixed_factor('rpt_aboody_overnight_sentiment_21d', {})
class Factor_rpt_aboody_overnight_sentiment_21d(BaseFactor):
    name = 'rpt_aboody_overnight_sentiment_21d'
    description = '隔夜收益情绪滚动移植'
    warmup_days = 22
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        value = (x['open_hfq']/x['close_hfq'].shift(1)-1).rolling(21).mean()
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
