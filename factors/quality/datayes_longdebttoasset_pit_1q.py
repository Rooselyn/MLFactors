"""通联 DataYes／优矿424因子库

公式：lt_borr_q/total_assets_q，q取最新已公告报告期；比例小数。；原目录：LongDebtToAsset；追踪：DY0115；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'lt_borr': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'lt_borr', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_longdebttoasset_pit_1q', 'engine': 'financial', 'expression': 'v1/v0', 'leaves': {'v0': ['financial_balance_sheet', 'total_assets', 'B', 0], 'v1': ['financial_balance_sheet', 'lt_borr', 'B', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_longdebttoasset_pit_1q', {})
class Factor_datayes_longdebttoasset_pit_1q(PublicFactor):
    name = 'datayes_longdebttoasset_pit_1q'
    description = 'lt_borr_q/total_assets_q，q取最新已公告报告期；比例小数。；原目录：LongDebtToAsset；追踪：DY0115；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
