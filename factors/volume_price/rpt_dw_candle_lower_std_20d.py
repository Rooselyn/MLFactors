"""蜡烛下影线标准差：x=(min(O,C)−L)/mean5(min(O,C)−L)；因子=std20(x)。

来源: [东吴《上下影线，蜡烛好还是威廉好？》PDF](https://github.com/hugo2046/QuantsPlaybook/blob/master/B-%E5%9B%A0%E5%AD%90%E6%9E%84%E5%BB%BA%E7%B1%BB/%E4%B8%8A%E4%B8%8B%E5%BD%B1%E7%BA%BF%E5%9B%A0%E5%AD%90/20200619-%E4%B8%9C%E5%90%B4%E8%AF%81%E5%88%B8-%E2%80%9C%E6%8A%80%E6%9C%AF%E5%88%86%E6%9E%90%E6%8B%A5%E6%8A%B1%E9%80%89%E8%82%A1%E5%9B%A0%E5%AD%90%E2%80%9D%E7%B3%BB%E5%88%97%E7%A0%94%E7%A9%B6%EF%BC%88%E4%BA%8C%EF%BC%89%EF%BC%9A%E4%B8%8A%E4%B8%8B%E5%BD%B1%E7%BA%BF%EF%BC%8C%E8%9C%A1%E7%83%9B%E5%A5%BD%E8%BF%98%E6%98%AF%E5%A8%81%E5%BB%89%E5%A5%BD%EF%BC%9F.pdf)
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
@fixed_factor('rpt_dw_candle_lower_std_20d', {})
class Factor_rpt_dw_candle_lower_std_20d(BaseFactor):
    name = 'rpt_dw_candle_lower_std_20d'
    description = '蜡烛下影线标准差'
    warmup_days = 24
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        shadow = np.minimum(x['open_hfq'],x['close_hfq'])-x['low_hfq']
        value = (shadow/shadow.rolling(5).mean().replace(0,np.nan)).rolling(20).std()
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
