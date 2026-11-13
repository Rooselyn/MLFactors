"""销售管理费用率指数：[(sell_exp+admin_exp)/revenue]_y / [(sell_exp+admin_exp)/revenue]_{y−1}；为A股费用映射版，不直接等同完整M-score。

来源: [Beneish原论文PDF](https://www.calctopia.com/papers/beneish1999.pdf)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'sell_exp': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'sell_exp', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'admin_exp': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'admin_exp', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'revenue': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'revenue', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_beneish_sgai_pit_1y', 'engine': 'financial', 'leaves': {'a': ['financial_income', 'sell_exp', 'Y', 0], 'b': ['financial_income', 'admin_exp', 'Y', 0], 'c': ['financial_income', 'sell_exp', 'Y', 4], 'd': ['financial_income', 'admin_exp', 'Y', 4], 'r': ['financial_income', 'revenue', 'Y', 0], 's': ['financial_income', 'revenue', 'Y', 4]}, 'annual': True, 'expression': '((a+b)/r)/((c+d)/s)'}

@register_factor
@fixed_factor('rpt_beneish_sgai_pit_1y', {})
class Factor_rpt_beneish_sgai_pit_1y(PublicFactor):
    name = 'rpt_beneish_sgai_pit_1y'
    description = '销售管理费用率指数'
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
        value = _formula_calculations.evaluate_expression('((a+b)/r)/((c+d)/s)', env)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
