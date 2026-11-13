"""销售增长减费用增长：g2(revenue)−g2(sell_exp+admin_exp)，g2(X)=X_y/[(X_{y−1}+X_{y−2})/2]−1。

来源: [GrSaleToGrOverhead／OSAP源码](https://github.com/OpenSourceAP/CrossSection/blob/master/Signals/LegacyStataCode/Predictors/GrSaleToGrOverhead.do)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'revenue': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'revenue', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'sell_exp': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'sell_exp', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'admin_exp': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'admin_exp', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_osap_sales_minus_overhead_growth_pit_2y', 'engine': 'financial', 'leaves': {'r0': ['financial_income', 'revenue', 'Y', 0], 'r4': ['financial_income', 'revenue', 'Y', 4], 'r8': ['financial_income', 'revenue', 'Y', 8], 's0': ['financial_income', 'sell_exp', 'Y', 0], 's4': ['financial_income', 'sell_exp', 'Y', 4], 's8': ['financial_income', 'sell_exp', 'Y', 8], 'a0': ['financial_income', 'admin_exp', 'Y', 0], 'a4': ['financial_income', 'admin_exp', 'Y', 4], 'a8': ['financial_income', 'admin_exp', 'Y', 8]}, 'annual': True, 'expression': 'r0/positive((r4+r8)/2)-(s0+a0)/positive((s4+a4+s8+a8)/2)'}

@register_factor
@fixed_factor('rpt_osap_sales_minus_overhead_growth_pit_2y', {})
class Factor_rpt_osap_sales_minus_overhead_growth_pit_2y(PublicFactor):
    name = 'rpt_osap_sales_minus_overhead_growth_pit_2y'
    description = '销售增长减费用增长'
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
        value = _formula_calculations.evaluate_expression('r0/positive((r4+r8)/2)-(s0+a0)/positive((s4+a4+s8+a8)/2)', env)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
