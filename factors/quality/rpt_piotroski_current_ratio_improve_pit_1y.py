"""F-score子信号：流动比率改善：1((total_cur_assets/total_cur_liab)_y>(total_cur_assets/total_cur_liab)_{y−1})。

来源: [Piotroski作者机构PDF](https://www.chicagobooth.edu/~/media/fe874ee65f624aaebd0166b1974fd74d.pdf)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'total_cur_assets': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_cur_assets', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'total_cur_liab': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_cur_liab', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_piotroski_current_ratio_improve_pit_1y', 'engine': 'financial', 'leaves': {'a': ['financial_balance_sheet', 'total_cur_assets', 'Y', 0], 'b': ['financial_balance_sheet', 'total_cur_liab', 'Y', 0], 'c': ['financial_balance_sheet', 'total_cur_assets', 'Y', 4], 'd': ['financial_balance_sheet', 'total_cur_liab', 'Y', 4]}, 'annual': True}

@register_factor
@fixed_factor('rpt_piotroski_current_ratio_improve_pit_1y', {})
class Factor_rpt_piotroski_current_ratio_improve_pit_1y(PublicFactor):
    name = 'rpt_piotroski_current_ratio_improve_pit_1y'
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
        left = _formula_calculations.evaluate_expression('a/positive(b)', env)
        right = _formula_calculations.evaluate_expression('c/positive(d)', env)
        value = (left > right).astype(float).where(left.notna())
        value = value.where(right.notna())
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
