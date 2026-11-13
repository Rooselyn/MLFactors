"""净营运资本占比变化：W_y=(total_cur_assets−c_cash_equ_end_period−total_cur_liab+st_borr+non_cur_liab_due_1y)/total_assets；W_y−W_{y−1}。

来源: [ChNWC／OSAP源码](https://github.com/OpenSourceAP/CrossSection/blob/master/Signals/LegacyStataCode/Predictors/ChNWC.do)
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
    'total_cur_liab': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_cur_liab', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'st_borr': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'st_borr', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'non_cur_liab_due_1y': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'non_cur_liab_due_1y', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'total_assets': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_assets', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_osap_net_working_capital_change_pit_1y', 'engine': 'financial', 'leaves': {'a0': ['financial_balance_sheet', 'total_cur_assets', 'Y', 0], 'c0': ['financial_cash_flow', 'c_cash_equ_end_period', 'Y', 0], 'l0': ['financial_balance_sheet', 'total_cur_liab', 'Y', 0], 's0': ['financial_balance_sheet', 'st_borr', 'Y', 0], 'n0': ['financial_balance_sheet', 'non_cur_liab_due_1y', 'Y', 0], 'x0': ['financial_balance_sheet', 'total_assets', 'Y', 0], 'a4': ['financial_balance_sheet', 'total_cur_assets', 'Y', 4], 'c4': ['financial_cash_flow', 'c_cash_equ_end_period', 'Y', 4], 'l4': ['financial_balance_sheet', 'total_cur_liab', 'Y', 4], 's4': ['financial_balance_sheet', 'st_borr', 'Y', 4], 'n4': ['financial_balance_sheet', 'non_cur_liab_due_1y', 'Y', 4], 'x4': ['financial_balance_sheet', 'total_assets', 'Y', 4]}, 'annual': True, 'expression': '(a0-c0-l0+s0+n0)/x0-(a4-c4-l4+s4+n4)/x4'}

@register_factor
@fixed_factor('rpt_osap_net_working_capital_change_pit_1y', {})
class Factor_rpt_osap_net_working_capital_change_pit_1y(PublicFactor):
    name = 'rpt_osap_net_working_capital_change_pit_1y'
    description = '净营运资本占比变化'
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
        value = _formula_calculations.evaluate_expression('(a0-c0-l0+s0+n0)/x0-(a4-c4-l4+s4+n4)/x4', env)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
