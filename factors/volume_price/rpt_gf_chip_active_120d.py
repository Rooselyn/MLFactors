"""活动筹码：近120日按信号日未复权价尺度建0.01元网格；f_d为[L,H]、众数C的离散三角密度；D_d=(1−clip(T_d,0,1))D_{d−1}+clip(T_d,0,1)V_df_d，D初值0；π=D/ΣD；输出Σ_{0.9C<p≤1.1C}π(p)。

来源: [广发《基于筹码分布的选股策略》／复现源码](https://github.com/hugo2046/QuantsPlaybook/blob/master/B-%E5%9B%A0%E5%AD%90%E6%9E%84%E5%BB%BA%E7%B1%BB/%E7%AD%B9%E7%A0%81%E5%9B%A0%E5%AD%90/scr/cyq.py)；[三角分布辅助源码](https://github.com/hugo2046/QuantsPlaybook/blob/master/B-%E5%9B%A0%E5%AD%90%E6%9E%84%E5%BB%BA%E7%B1%BB/%E7%AD%B9%E7%A0%81%E5%9B%A0%E5%AD%90/scr/distribution_of_chips.py)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'high_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'high_hfq'),
    'low_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'low_hfq'),
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
    'close': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close'),
    'vol': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'vol'),
    'turnover_rate': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'turnover_rate'),
}

def chip(high, low, close, raw_close, volume, turnover, operation):
    result = close * np.nan
    for symbol in close:
        values = np.column_stack([v[symbol] for v in (high, low, close, raw_close, volume, turnover)])
        for i in range(119, len(values)):
            window = values[i-119:i+1]
            if not np.isfinite(window).all() or (window[:,5] < 0).any(): continue
            scale = window[-1,3]/window[-1,2]
            h,l,c = (window[:,j]*scale for j in (0,1,2))
            grid = np.arange(np.floor(l.min()*100), np.ceil(h.max()*100)+1)/100
            density = np.zeros(len(grid))
            for hh,ll,cc,vv,tt in zip(h,l,c,window[:,4],window[:,5]):
                if hh < ll or not ll <= cc <= hh: break
                if hh == ll:
                    f = (np.arange(len(grid)) == np.abs(grid-cc).argmin()).astype(float)
                else:
                    # Discrete triangular law, including endpoint modes.
                    left = (grid-ll)/(cc-ll) if cc>ll else np.ones(len(grid))
                    right = (hh-grid)/(hh-cc) if hh>cc else np.ones(len(grid))
                    f = np.minimum(left,right).clip(0)
                    if f.sum() == 0: f[np.abs(grid-cc).argmin()] = 1
                    f /= f.sum()
                tt = np.clip(tt,0,1)
                density = (1-tt)*density + tt*vv*f
            else:
                if density.sum() <= 0: continue
                prob = density/density.sum(); current = window[-1,3]
                if operation == 'winning': answer = prob[grid<=current].sum()
                elif operation == 'active': answer = prob[(grid>.9*current)&(grid<=1.1*current)].sum()
                else:
                    below = grid[np.cumsum(prob)<.5]
                    answer = current/below[-1]-1 if len(below) and below[-1]>0 else np.nan
                result.loc[result.index[i],symbol] = answer
    return result

@register_factor
@fixed_factor('rpt_gf_chip_active_120d', {})
class Factor_rpt_gf_chip_active_120d(BaseFactor):
    name = 'rpt_gf_chip_active_120d'
    description = '活动筹码'
    warmup_days = 119
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        value = chip(x['high_hfq'],x['low_hfq'],x['close_hfq'],x['close'],x['vol']*100,x['turnover_rate']/100,'active')
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
