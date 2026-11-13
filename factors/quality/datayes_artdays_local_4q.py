"""通联 DataYes／优矿424因子库

公式：365×AVG4(accounts_receiv)/T(revenue)；周转天数固定365日年化，TTM金额≤0为NaN。；原目录：ARTDays；追踪：DY0305；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'revenue': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'revenue', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'accounts_receiv': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'accounts_receiv', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_artdays_local_4q', 'engine': 'financial', 'expression': '365 * v0 / positive(v1)', 'leaves': {'v0': ['financial_balance_sheet', 'accounts_receiv', 'AVG4', 0], 'v1': ['financial_income', 'revenue', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_artdays_local_4q', {})
class Factor_datayes_artdays_local_4q(PublicFactor):
    name = 'datayes_artdays_local_4q'
    description = '365×AVG4(accounts_receiv)/T(revenue)；周转天数固定365日年化，TTM金额≤0为NaN。；原目录：ARTDays；追踪：DY0305；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
