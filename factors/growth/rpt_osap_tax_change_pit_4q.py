"""单季所得税同比变化：[income_tax_Q(q)−income_tax_Q(q−4)]/total_assets_{q−4}。

来源: [ChTax／OSAP源码](https://github.com/OpenSourceAP/CrossSection/blob/master/Signals/LegacyStataCode/Predictors/ChTax.do)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'income_tax': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'income_tax', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'total_assets': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_assets', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_osap_tax_change_pit_4q', 'engine': 'financial', 'leaves': {'n': ['financial_income', 'income_tax', 'Q', 0], 'm': ['financial_income', 'income_tax', 'Q', 4], 'a': ['financial_balance_sheet', 'total_assets', 'B', 4]}, 'annual': False, 'expression': '(n-m)/a'}

@register_factor
@fixed_factor('rpt_osap_tax_change_pit_4q', {})
class Factor_rpt_osap_tax_change_pit_4q(PublicFactor):
    name = 'rpt_osap_tax_change_pit_4q'
    description = '单季所得税同比变化'
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
        value = _formula_calculations.evaluate_expression('(n-m)/a', env)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
