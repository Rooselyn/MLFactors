"""经营流动资产变动：Δ_y(total_cur_assets−c_cash_equ_end_period)/avg(total_assets_y,total_assets_{y−1})。

来源: [DelCOA／OSAP源码](https://github.com/OpenSourceAP/CrossSection/blob/master/Signals/LegacyStataCode/Predictors/DelCOA.do)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'total_cur_assets': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_cur_assets', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'c_cash_equ_end_period': ParquetInput("MLFactors/data/zz500/financial_cash_flow/*/*.parquet", 'c_cash_equ_end_period', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'total_assets': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_assets', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_osap_operating_current_assets_change_pit_1y', 'engine': 'financial', 'leaves': {'a': ['financial_balance_sheet', 'total_cur_assets', 'Y', 0], 'c': ['financial_cash_flow', 'c_cash_equ_end_period', 'Y', 0], 'b': ['financial_balance_sheet', 'total_cur_assets', 'Y', 4], 'd': ['financial_cash_flow', 'c_cash_equ_end_period', 'Y', 4], 'x': ['financial_balance_sheet', 'total_assets', 'Y', 0], 'y': ['financial_balance_sheet', 'total_assets', 'Y', 4]}, 'annual': True, 'expression': '((a-c)-(b-d))/((x+y)/2)'}

@register_factor
@fixed_factor('rpt_osap_operating_current_assets_change_pit_1y', {})
class Factor_rpt_osap_operating_current_assets_change_pit_1y(PublicFactor):
    name = 'rpt_osap_operating_current_assets_change_pit_1y'
    description = '经营流动资产变动'
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
        value = _formula_calculations.evaluate_expression('((a-c)-(b-d))/((x+y)/2)', env)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
