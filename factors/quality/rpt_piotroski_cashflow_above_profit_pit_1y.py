"""F-score子信号：现金流超过利润：1(n_cashflow_act_y>n_income_y)。

来源: [Piotroski作者机构PDF](https://www.chicagobooth.edu/~/media/fe874ee65f624aaebd0166b1974fd74d.pdf)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'n_cashflow_act': ParquetInput("MLFactors/data/zz500/financial_cash_flow/*/*.parquet", 'n_cashflow_act', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'n_income': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'n_income', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_piotroski_cashflow_above_profit_pit_1y', 'engine': 'financial', 'leaves': {'c': ['financial_cash_flow', 'n_cashflow_act', 'Y', 0], 'n': ['financial_income', 'n_income', 'Y', 0]}, 'annual': True}

@register_factor
@fixed_factor('rpt_piotroski_cashflow_above_profit_pit_1y', {})
class Factor_rpt_piotroski_cashflow_above_profit_pit_1y(PublicFactor):
    name = 'rpt_piotroski_cashflow_above_profit_pit_1y'
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
        left = _formula_calculations.evaluate_expression('c', env)
        right = _formula_calculations.evaluate_expression('n', env)
        value = (left > right).astype(float).where(left.notna())
        value = value.where(right.notna())
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
