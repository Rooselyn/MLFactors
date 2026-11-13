"""通联 DataYes／优矿424因子库

公式：QY(ass_invest_income)/QY(total_profit)，同一报告期YTD相除。；原目录：InvestRAssociatesToTPLatest；追踪：DY0172；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'ass_invest_income': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'ass_invest_income', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'total_profit': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'total_profit', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_investrassociatestotplatest_local_1q', 'engine': 'financial', 'expression': 'v0/v1', 'leaves': {'v0': ['financial_income', 'ass_invest_income', 'QY', 0], 'v1': ['financial_income', 'total_profit', 'QY', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_investrassociatestotplatest_local_1q', {})
class Factor_datayes_investrassociatestotplatest_local_1q(PublicFactor):
    name = 'datayes_investrassociatestotplatest_local_1q'
    description = 'QY(ass_invest_income)/QY(total_profit)，同一报告期YTD相除。；原目录：InvestRAssociatesToTPLatest；追踪：DY0172；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
