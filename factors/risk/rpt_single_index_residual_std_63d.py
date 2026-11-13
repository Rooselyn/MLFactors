"""单指数残差波动：近63日OLS：r_i=α+βr_b+ε；输出std(ε)，r_b为000905.SH日收益。

来源: [Ang等相关原论文PDF](https://www.ruf.rice.edu/~yxing/AHXZ_011906.pdf)；[中国股票特征定义表](https://github.com/Quantactix/ChinaAShareEquityCharacteristics/blob/master/char_list.csv)
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
@fixed_factor('rpt_single_index_residual_std_63d', {})
class Factor_rpt_single_index_residual_std_63d(BaseFactor):
    name = 'rpt_single_index_residual_std_63d'
    description = '单指数残差波动'
    warmup_days = 63
    INPUTS = INPUTS

    def __init__(self):
        pass

    def generate_signals(self, data, constituents=None):
        x, dates, symbols = panels(data, self.INPUTS)
        eligible = eligibility(data, dates, symbols)
        r=x['close_hfq'].pct_change(fill_method=None);market=x['benchmark_close'].iloc[:,0].pct_change(fill_method=None)
        value=r*np.nan
        for i in range(63,len(dates)):
            b=market.iloc[i-62:i+1].to_numpy();design=np.column_stack([np.ones(63),b])
            if not np.isfinite(design).all() or np.linalg.matrix_rank(design)<2:continue
            for symbol in symbols:
                y=r[symbol].iloc[i-62:i+1].to_numpy()
                if not np.isfinite(y).all():continue
                error=y-design@np.linalg.lstsq(design,y,rcond=None)[0]
                value.loc[dates[i],symbol]=pd.Series(error).std()
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligible).rename_axis(index='date',columns='symbol')
