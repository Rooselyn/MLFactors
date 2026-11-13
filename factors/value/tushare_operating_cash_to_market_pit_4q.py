"""Tushare 自研因子库（公开目录，剔除重复Alpha101）

公式：TTM(n_cashflow_act)/MC；原目录：ocf_to_market；追踪：PF02686；[来源](https://tushare.pro/document/2?doc_id=486)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_mv': ParquetInput('MLFactors/data/zz500/stock_day/*/*.parquet', 'total_mv'),
    'n_cashflow_act': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_cashflow_act', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'tushare_operating_cash_to_market_pit_4q', 'engine': 'financial', 'expression': 'v0/MC', 'leaves': {'v0': ['financial_cash_flow', 'n_cashflow_act', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('tushare_operating_cash_to_market_pit_4q', {})
class Factor_tushare_operating_cash_to_market_pit_4q(PublicFactor):
    name = 'tushare_operating_cash_to_market_pit_4q'
    description = 'TTM(n_cashflow_act)/MC；原目录：ocf_to_market；追踪：PF02686；[来源](https://tushare.pro/document/2?doc_id=486)。'
    INPUTS = INPUTS
    SPEC = SPEC
