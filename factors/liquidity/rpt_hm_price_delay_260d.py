"""价格延迟滚动移植：每日以t为锚，R_{i,j}=C_{i,t−5j}/C_{i,t−5(j+1)}−1，j=0,…,55，基准000905.SH同法；用j=0,…,51的52个块收益估计R_{i,j}=α+β_0R_{b,j}+Σ_{k=1}^4β_kR_{b,j+k}+ε_j；D=1−R²_restricted/R²_full，restricted仅含当期基准。

来源: [Hou–Moskowitz原论文PDF](https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2019/09/MarketFrictionsPriceDelayandtheCross-SectionofExpectedReturns.pdf)
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
@fixed_factor('rpt_hm_price_delay_260d', {})
class Factor_rpt_hm_price_delay_260d(BaseFactor):
    name = 'rpt_hm_price_delay_260d'
    description = '价格延迟滚动移植'
    warmup_days = 281
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        c=x['close_hfq']; bench=x['benchmark_close'].iloc[:,0]
        value=c*np.nan
        for i in range(280,len(dates)):
            end=i-5*np.arange(56); begin=end-5
            market=bench.iloc[end].to_numpy()/bench.iloc[begin].to_numpy()-1
            design=np.column_stack([np.ones(52)]+[market[k:k+52] for k in range(5)])
            if not np.isfinite(design).all() or np.linalg.matrix_rank(design)<6:continue
            for symbol in symbols:
                y=c[symbol].iloc[end[:52]].to_numpy()/c[symbol].iloc[begin[:52]].to_numpy()-1
                if not np.isfinite(y).all():continue
                tss=np.sum((y-y.mean())**2)
                if tss<=0:continue
                full=1-np.sum((y-design@np.linalg.lstsq(design,y,rcond=None)[0])**2)/tss
                restricted=design[:,:2]
                short=1-np.sum((y-restricted@np.linalg.lstsq(restricted,y,rcond=None)[0])**2)/tss
                if full>0:value.loc[dates[i],symbol]=1-short/full
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
