"""销售增长减存货增长：g2(X)=X_y/[(X_{y−1}+X_{y−2})/2]−1；g2(revenue)−g2(inventories)；固定完整三年，不启用单年回退。

来源: [GrSaleToGrInv／OSAP源码](https://github.com/OpenSourceAP/CrossSection/blob/master/Signals/LegacyStataCode/Predictors/GrSaleToGrInv.do)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'revenue': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'revenue', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'inventories': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'inventories', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_osap_sales_minus_inventory_growth_pit_2y', 'engine': 'financial', 'leaves': {'r0': ['financial_income', 'revenue', 'Y', 0], 'r4': ['financial_income', 'revenue', 'Y', 4], 'r8': ['financial_income', 'revenue', 'Y', 8], 'x0': ['financial_balance_sheet', 'inventories', 'Y', 0], 'x4': ['financial_balance_sheet', 'inventories', 'Y', 4], 'x8': ['financial_balance_sheet', 'inventories', 'Y', 8]}, 'annual': True, 'expression': 'r0/positive((r4+r8)/2)-x0/positive((x4+x8)/2)'}

@register_factor
@fixed_factor('rpt_osap_sales_minus_inventory_growth_pit_2y', {})
class Factor_rpt_osap_sales_minus_inventory_growth_pit_2y(PublicFactor):
    name = 'rpt_osap_sales_minus_inventory_growth_pit_2y'
    description = '销售增长减存货增长'
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
        value = _formula_calculations.evaluate_expression('r0/positive((r4+r8)/2)-x0/positive((x4+x8)/2)', env)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
