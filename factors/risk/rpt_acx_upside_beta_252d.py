"""上行贝塔：近252日，β=cov(r_i,r_b∣r_b>mean252(r_b))/var(r_b∣同条件)。

来源: [Ang–Chen–Xing《Downside Risk》PDF](https://www.ruf.rice.edu/~yxing/downside.pdf)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
    'benchmark_close': ParquetInput("MLFactors/data/zz500/zz500_daily_index/*/*.parquet", 'close', date_column='trade_date', symbol_column=None, expression='close', filters=(('ts_code', '000905.SH'),)),
}


@register_factor
@fixed_factor('rpt_acx_upside_beta_252d', {})
class Factor_rpt_acx_upside_beta_252d(BaseFactor):
    name = 'rpt_acx_upside_beta_252d'
    description = '上行贝塔'
    warmup_days = 252
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        r=x['close_hfq'].pct_change(fill_method=None); market=x['benchmark_close'].iloc[:,0].pct_change(fill_method=None)
        value=r*np.nan
        for i in range(252,len(dates)):
            b=market.iloc[i-251:i+1]; select=b > b.mean()
            if b.notna().sum()!=252 or select.sum()<30:continue
            a=r.iloc[i-251:i+1]
            good=a.notna().all()
            variance=b[select].var(ddof=1)
            if variance>0:value.loc[dates[i],good]=a.loc[select,good].apply(lambda y:y.cov(b[select])/variance)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
