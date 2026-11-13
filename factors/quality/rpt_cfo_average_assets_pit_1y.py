"""现金流/平均资产：n_cashflow_act_y/[(total_assets_y+total_assets_{y−1})/2]。

来源: [Sloan资产负债表应计原式／OSAP](https://github.com/OpenSourceAP/CrossSection/blob/master/Signals/LegacyStataCode/Predictors/Accruals.do)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'n_cashflow_act': ParquetInput("MLFactors/data/zz500/financial_cash_flow/*/*.parquet", 'n_cashflow_act', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'total_assets': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_assets', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_cfo_average_assets_pit_1y', 'engine': 'financial', 'leaves': {'c': ['financial_cash_flow', 'n_cashflow_act', 'Y', 0], 'a': ['financial_balance_sheet', 'total_assets', 'Y', 0], 'b': ['financial_balance_sheet', 'total_assets', 'Y', 4]}, 'annual': True, 'expression': 'c/((a+b)/2)'}

@register_factor
@fixed_factor('rpt_cfo_average_assets_pit_1y', {})
class Factor_rpt_cfo_average_assets_pit_1y(PublicFactor):
    name = 'rpt_cfo_average_assets_pit_1y'
    description = '现金流/平均资产'
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
        value = _formula_calculations.evaluate_expression('c/((a+b)/2)', env)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
