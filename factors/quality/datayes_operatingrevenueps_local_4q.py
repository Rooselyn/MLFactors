"""通联 DataYes／优矿424因子库

公式：T(revenue)/B(total_share)，TTM金额/同锚报告期末总股本，元/股；不是加权每股收益。；原目录：OperatingRevenuePS；追踪：DY0234；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_share': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'total_share', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_operatingrevenueps_local_4q', 'engine': 'financial', 'expression': 'v0/v1', 'leaves': {'v0': ['financial_income', 'revenue', 'T', 0], 'v1': ['financial_balance_sheet', 'total_share', 'B', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_operatingrevenueps_local_4q', {})
class Factor_datayes_operatingrevenueps_local_4q(PublicFactor):
    name = 'datayes_operatingrevenueps_local_4q'
    description = 'T(revenue)/B(total_share)，TTM金额/同锚报告期末总股本，元/股；不是加权每股收益。；原目录：OperatingRevenuePS；追踪：DY0234；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
