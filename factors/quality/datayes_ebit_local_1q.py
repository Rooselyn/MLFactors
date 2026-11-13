"""通联 DataYes／优矿424因子库

公式：QY(ebit)；取最新一期已公告利润表的原始年度累计金额（元），不年化、不把它当单季。；原目录：EBIT；追踪：DY0357；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'ebit': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'ebit', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_ebit_local_1q', 'engine': 'financial', 'expression': 'v0', 'leaves': {'v0': ['financial_income', 'ebit', 'QY', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_ebit_local_1q', {})
class Factor_datayes_ebit_local_1q(PublicFactor):
    name = 'datayes_ebit_local_1q'
    description = 'QY(ebit)；取最新一期已公告利润表的原始年度累计金额（元），不年化、不把它当单季。；原目录：EBIT；追踪：DY0357；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
