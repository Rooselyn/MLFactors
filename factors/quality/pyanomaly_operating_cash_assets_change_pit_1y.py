"""PyAnomaly

公式：ocf_y/at_y−ocf_{y−1}/at_{y−1}；符号物理映射：ocf=n_cashflow_act, at=total_assets；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：FUNDA.ocf_at_chg1；追踪：PF02126；[来源](https://github.com/chulwoohan/pyanomaly)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'n_cashflow_act': ParquetInput('MLFactors/data/zz500/financial_cash_flow/*/*.parquet', 'n_cashflow_act', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'pyanomaly_operating_cash_assets_change_pit_1y', 'engine': 'financial', 'expression': 'v0/v1-v2/v3', 'leaves': {'v0': ['financial_cash_flow', 'n_cashflow_act', 'Y', 0], 'v1': ['financial_balance_sheet', 'total_assets', 'Y', 0], 'v2': ['financial_cash_flow', 'n_cashflow_act', 'Y', 4], 'v3': ['financial_balance_sheet', 'total_assets', 'Y', 4]}, 'annual': True, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('pyanomaly_operating_cash_assets_change_pit_1y', {})
class Factor_pyanomaly_operating_cash_assets_change_pit_1y(PublicFactor):
    name = 'pyanomaly_operating_cash_assets_change_pit_1y'
    description = 'ocf_y/at_y−ocf_{y−1}/at_{y−1}；符号物理映射：ocf=n_cashflow_act, at=total_assets；y为已公告完整财年，q为单季，lag_y/lag_q只按报告期编号匹配，不按记录条数跳过缺期。；原目录：FUNDA.ocf_at_chg1；追踪：PF02126；[来源](https://github.com/chulwoohan/pyanomaly)。'
    INPUTS = INPUTS
    SPEC = SPEC
