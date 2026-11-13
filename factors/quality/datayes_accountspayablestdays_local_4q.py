"""通联 DataYes／优矿424因子库

公式：365×AVG4(acct_payable)/T(oper_cost)；周转天数固定365日年化，TTM金额≤0为NaN。；原目录：AccountsPayablesTDays；追踪：DY0307；[来源](https://uqer.datayes.com/help/appendixFactors/)。
实现约定见公开因子库报告；共享数值实现位于已有的 factors/base.py。
"""
from factors.inputs import ParquetInput, fixed_factor
from factors.registry import register_factor
from factors.base import PublicFactor

INPUTS = {
    'oper_cost': ParquetInput('MLFactors/data/zz500/financial_income/*/*.parquet', 'oper_cost', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
    'acct_payable': ParquetInput('MLFactors/data/zz500/financial_balance_sheet/*/*.parquet', 'acct_payable', date_column="ann_date", announcement_columns=("f_ann_date", "ann_date"), filters=(("report_type", "1"),)),
}
SPEC = {'name': 'datayes_accountspayablestdays_local_4q', 'engine': 'financial', 'expression': '365 * v0 / positive(v1)', 'leaves': {'v0': ['financial_balance_sheet', 'acct_payable', 'AVG4', 0], 'v1': ['financial_income', 'oper_cost', 'T', 0]}, 'annual': False, 'daily_lag': 0, 'rank': False}

@register_factor
@fixed_factor('datayes_accountspayablestdays_local_4q', {})
class Factor_datayes_accountspayablestdays_local_4q(PublicFactor):
    name = 'datayes_accountspayablestdays_local_4q'
    description = '365×AVG4(acct_payable)/T(oper_cost)；周转天数固定365日年化，TTM金额≤0为NaN。；原目录：AccountsPayablesTDays；追踪：DY0307；[来源](https://uqer.datayes.com/help/appendixFactors/)。'
    INPUTS = INPUTS
    SPEC = SPEC
