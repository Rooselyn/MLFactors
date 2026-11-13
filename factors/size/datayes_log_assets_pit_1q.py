"""通联 DataYes／优矿424因子库

公式：log(total_assets_q)，q为截至t已公告的最新报告期，资产以元计且>0。；原目录：ASSI；追踪：DY0035；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'total_assets': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_assets', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_log_assets_pit_1q', 'engine': 'financial', 'expression': 'log(v0)', 'leaves': {'v0': ['financial_balance_sheet', 'total_assets', 'B', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_log_assets_pit_1q', {})
class Factor_datayes_log_assets_pit_1q(PublicFactor):
    name = 'datayes_log_assets_pit_1q'
    description = 'log(total_assets_q)，q为截至t已公告的最新报告期，资产以元计且>0。；原目录：ASSI；追踪：DY0035；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
