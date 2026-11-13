"""账面市值比：total_hldr_eqy_exc_min_int_latest/MV_t；账面值用最新已公告报告期，市值每天更新；本地PIT版本。

来源: [Fama–French账面市值比定义](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/variable_definitions.html)；[BM／OSAP源码](https://github.com/OpenSourceAP/CrossSection/blob/master/Signals/LegacyStataCode/Predictors/BM.do)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'total_hldr_eqy_exc_min_int': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_hldr_eqy_exc_min_int', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'total_mv': ParquetInput("MLFactors/data/zz500/stock_day/*/*.parquet", 'total_mv'),
}
SPEC = {'name': 'rpt_book_to_market_local_pit_1q', 'engine': 'financial', 'leaves': {'b': ['financial_balance_sheet', 'total_hldr_eqy_exc_min_int', 'B', 0]}, 'annual': False, 'expression': 'b/MC'}

@register_factor
@fixed_factor('rpt_book_to_market_local_pit_1q', {})
class Factor_rpt_book_to_market_local_pit_1q(PublicFactor):
    name = 'rpt_book_to_market_local_pit_1q'
    description = '账面市值比'
    warmup_days = 100000
    INPUTS = INPUTS

    def __init__(self):
        pass

    SPEC = SPEC

    def generate_signals(self, data, constituents=None):
        dates = pd.DatetimeIndex(data.index.get_level_values('date').unique()).sort_values()
        symbols = data.index.get_level_values('symbol').unique().sort_values()
        reports = _formula_calculations.read_reports(self.INPUTS,end=dates.max(),symbols=list(symbols))
        env, self.available_ann_dates = _formula_calculations.leaf_panels(self.SPEC,reports,dates,symbols,return_available=True)
        env['MC'] = data['total_mv'].unstack('symbol').reindex(index=dates,columns=symbols).where(lambda v:v>0)*10000
        value = _formula_calculations.evaluate_expression('b/MC', env)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
