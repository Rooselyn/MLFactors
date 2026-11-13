"""F-score子信号：资产周转改善：1(revenue_y/A_{y−1}>revenue_{y−1}/A_{y−2})。

来源: [Piotroski作者机构PDF](https://www.chicagobooth.edu/~/media/fe874ee65f624aaebd0166b1974fd74d.pdf)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'revenue': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'revenue', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'total_assets': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_assets', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_piotroski_asset_turnover_improve_pit_1y', 'engine': 'financial', 'leaves': {'r': ['financial_income', 'revenue', 'Y', 0], 'a': ['financial_balance_sheet', 'total_assets', 'Y', 4], 's': ['financial_income', 'revenue', 'Y', 4], 'b': ['financial_balance_sheet', 'total_assets', 'Y', 8]}, 'annual': True}

@register_factor
@fixed_factor('rpt_piotroski_asset_turnover_improve_pit_1y', {})
class Factor_rpt_piotroski_asset_turnover_improve_pit_1y(PublicFactor):
    name = 'rpt_piotroski_asset_turnover_improve_pit_1y'
    description = 'F-score子信号'
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
        left = _formula_calculations.evaluate_expression('r/a', env)
        right = _formula_calculations.evaluate_expression('s/b', env)
        value = (left > right).astype(float).where(left.notna())
        value = value.where(right.notna())
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
