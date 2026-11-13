"""经营利润/权益：OP_y=revenue_y−oper_cost_y−sell_exp_y−admin_exp_y−fin_exp_int_exp_y；OP_y/total_hldr_eqy_inc_min_int_y。

来源: [中国A股特征库定义表](https://github.com/Quantactix/ChinaAShareEquityCharacteristics/blob/master/char_list.csv)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from factors.base import PublicFactor, eligibility, _formula_calculations
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor

INPUTS = {
    'revenue': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'revenue', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'oper_cost': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'oper_cost', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'sell_exp': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'sell_exp', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'admin_exp': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'admin_exp', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'fin_exp_int_exp': ParquetInput("MLFactors/data/zz500/financial_income/*/*.parquet", 'fin_exp_int_exp', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
    'total_hldr_eqy_inc_min_int': ParquetInput("MLFactors/data/zz500/financial_balance_sheet/*/*.parquet", 'total_hldr_eqy_inc_min_int', date_column='ann_date', announcement_columns=('f_ann_date', 'ann_date'), filters=(('report_type', '1'),)),
}
SPEC = {'name': 'rpt_ashare_operating_profit_equity_pit_1y', 'engine': 'financial', 'leaves': {'r': ['financial_income', 'revenue', 'Y', 0], 'c': ['financial_income', 'oper_cost', 'Y', 0], 's': ['financial_income', 'sell_exp', 'Y', 0], 'g': ['financial_income', 'admin_exp', 'Y', 0], 'i': ['financial_income', 'fin_exp_int_exp', 'Y', 0], 'a': ['financial_balance_sheet', 'total_hldr_eqy_inc_min_int', 'Y', 0]}, 'annual': True, 'expression': '(r-c-s-g-i)/a'}

@register_factor
@fixed_factor('rpt_ashare_operating_profit_equity_pit_1y', {})
class Factor_rpt_ashare_operating_profit_equity_pit_1y(PublicFactor):
    name = 'rpt_ashare_operating_profit_equity_pit_1y'
    description = '经营利润/权益'
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
        value = _formula_calculations.evaluate_expression('(r-c-s-g-i)/a', env)
        return value.astype(float).replace([np.inf,-np.inf],np.nan).where(eligibility(data,dates,symbols)).rename_axis(index='date',columns='symbol')
