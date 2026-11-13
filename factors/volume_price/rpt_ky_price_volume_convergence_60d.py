"""量价双收敛：Z(F_C)+Z(F_V)；F定义为各自现值与5/10/20/60日MA的−ln(1+样本标准差)。

来源: [开源原报正文](https://www.fxbaogao.com/detail/4220842)；[开源《形态识别，均线的收敛与发散》／复现源码](https://github.com/hugo2046/QuantsPlaybook/blob/master/B-%E5%9B%A0%E5%AD%90%E6%9E%84%E5%BB%BA%E7%B1%BB/%E5%BC%80%E6%BA%90%E8%AF%81%E5%88%B8-%E5%BC%80%E6%BA%90%E9%87%8F%E5%8C%96%E8%AF%84%E8%AE%BA%EF%BC%8891%EF%BC%89%EF%BC%9A%E5%BD%A2%E6%80%81%E8%AF%86%E5%88%AB%EF%BC%8C%E5%9D%87%E7%BA%BF%E7%9A%84%E6%94%B6%E6%95%9B%E4%B8%8E%E5%8F%91%E6%95%A3/FactorArithmetic/convergence_factor.py)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import BaseFactor, panels, eligibility
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'close_hfq': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'close_hfq'),
    'vol': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'vol'),
}

def z(x, eligible=None, winsor=False):
    x = x.where(eligible) if eligible is not None else x.copy()
    if winsor:
        x = x.clip(x.quantile(.01, axis=1), x.quantile(.99, axis=1), axis=0)
    return x.sub(x.mean(axis=1), axis=0).div(x.std(axis=1, ddof=1).replace(0, np.nan), axis=0)

def convergence(x):
    values = np.stack([x.to_numpy()] + [x.rolling(w).mean().to_numpy() for w in (5,10,20,60)])
    return pd.DataFrame(-np.log1p(np.std(values, axis=0, ddof=1)), index=x.index, columns=x.columns)

@register_factor
@fixed_factor('rpt_ky_price_volume_convergence_60d', {})
class Factor_rpt_ky_price_volume_convergence_60d(BaseFactor):
    name = 'rpt_ky_price_volume_convergence_60d'
    description = '量价双收敛'
    warmup_days = 59
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        value = z(convergence(x['close_hfq']),eligible)+z(convergence(x['vol']*100),eligible)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
